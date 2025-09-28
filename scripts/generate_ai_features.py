import pandas as pd
import torch
import numpy as np
from pathlib import Path
from transformers import pipeline
from sentence_transformers import SentenceTransformer
from sklearn.cluster import DBSCAN
from tqdm import tqdm

tqdm.pandas()

def categorize_articles(df, batch_size=16):
    """Categorizes articles using a zero-shot classification model."""
    print("Categorizing articles...")
    classifier = pipeline(
        "zero-shot-classification",
        model="facebook/bart-large-mnli",
        device=0 if torch.cuda.is_available() else -1
    )
    categories = ["sports", "lifestyle", "music", "finance", "technology", "general news"]
    
    results = []
    for i in tqdm(range(0, len(df), batch_size), desc="Categorizing Batches"):
        batch = df['text_for_ai'][i:i+batch_size].tolist()
        results.extend(classifier(batch, candidate_labels=categories, multi_label=False))
        
    df['category'] = [res['labels'][0] for res in results]
    return df

def generate_embeddings_and_clusters(df, batch_size=32):
    """Generates vector embeddings and then clusters articles."""
    print("Generating embeddings...")
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    model = SentenceTransformer('all-MiniLM-L6-v2', device=device)
    
    embeddings = model.encode(
        df['text_for_ai'].tolist(),
        batch_size=batch_size,
        show_progress_bar=True
    )
    
    # Store the embeddings first (converted to list for MongoDB)
    df['embedding'] = [emb.tolist() for emb in embeddings]

    print("Clustering articles to find similar stories...")
    # Normalize embeddings for cosine similarity
    embeddings_norm = embeddings / np.linalg.norm(embeddings, axis=1, keepdims=True)
    
    clustering = DBSCAN(eps=0.3, min_samples=2, metric='cosine').fit(embeddings_norm)
    
    # Add the cluster ID to each article
    df['cluster_id'] = clustering.labels_
    
    return df

def main():
    """Main function to run the AI feature generation pipeline."""
    data_dir = Path("../data")
    input_path = data_dir / "cleaned_news.csv"
    output_path = data_dir / "enriched_news.pkl"

    print("Step 1: Loading cleaned data...")
    df = pd.read_csv(input_path)
    df['text_for_ai'] = df['title'] + ". " + df['summary'].fillna('')

    print("Step 2: Starting AI feature generation...")
    df = categorize_articles(df)
    df = generate_embeddings_and_clusters(df)
    
    df = df.drop(columns=['text_for_ai'])
    
    print(f"\nStep 3: Saving enriched data with clusters to {output_path}...")
    df.to_pickle(output_path)
    print("Done.")

if __name__ == "__main__":
    main()