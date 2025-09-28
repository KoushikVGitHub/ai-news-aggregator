import pandas as pd
import torch
import numpy as np
from pathlib import Path
from transformers import pipeline
from sentence_transformers import SentenceTransformer
from sklearn.cluster import DBSCAN
from tqdm import tqdm

# --- CONFIGURATION ---
DATA_DIR = Path("../data")
INPUT_FILE = DATA_DIR / "cleaned_news.csv"
CATEGORIES = ["sports", "lifestyle", "music", "finance", "technology", "general news"]
HIGHLIGHT_KEYWORDS = ['breaking', 'urgent', 'alert', 'exclusive', 'update']

# --- HELPER FUNCTIONS ---

def load_data(filepath):
    """Loads the cleaned news data from a CSV file."""
    print(f"Step 1: Loading cleaned data from {filepath}...")
    if not filepath.exists():
        raise FileNotFoundError(f"The file {filepath} was not found. Please run the previous scripts first.")
    df = pd.read_csv(filepath)
    # Create a single text field for AI processing
    df['text_for_ai'] = df['title'].fillna('') + ". " + df['summary'].fillna('')
    return df

def categorize_articles(df, batch_size=16):
    """Categorizes articles using a zero-shot classification model."""
    print("Step 2: Categorizing articles...")
    classifier = pipeline(
        "zero-shot-classification",
        model="facebook/bart-large-mnli",
        device=0 if torch.cuda.is_available() else -1
    )
    
    results = []
    # Process in batches for efficiency
    for i in tqdm(range(0, len(df), batch_size), desc="Categorizing Batches"):
        batch = df['text_for_ai'][i:i+batch_size].tolist()
        results.extend(classifier(batch, candidate_labels=CATEGORIES, multi_label=False))
        
    df['category'] = [res['labels'][0] for res in results]
    return df

def generate_and_cluster_articles(df, batch_size=32):
    """Generates vector embeddings and then clusters articles to find similar stories."""
    print("Step 3: Generating embeddings...")
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    model = SentenceTransformer('all-MiniLM-L6-v2', device=device)
    
    embeddings = model.encode(
        df['text_for_ai'].tolist(),
        batch_size=batch_size,
        show_progress_bar=True
    )
    
    print("Step 4: Clustering articles to find similar stories...")
    # Normalize embeddings for cosine similarity
    embeddings_norm = embeddings / np.linalg.norm(embeddings, axis=1, keepdims=True)
    
    # DBSCAN is great for this as it doesn't require a set number of clusters
    # The 'eps' parameter is crucial and may require tuning (0.2-0.4 is a good range)
    clustering = DBSCAN(eps=0.3, min_samples=2, metric='cosine').fit(embeddings_norm)
    
    df['cluster_id'] = clustering.labels_
    return df

def generate_highlights(df):
    """Scores and ranks story clusters to generate highlights."""
    print("Step 5: Scoring and generating highlights...")
    
    # Filter out unique articles (noise points from clustering)
    stories_df = df[df['cluster_id'] != -1].copy()
    
    highlights = []
    
    for cluster_id in stories_df['cluster_id'].unique():
        cluster_articles = stories_df[stories_df['cluster_id'] == cluster_id]
        
        # --- Scoring Logic ---
        # 1. Frequency Score (how many sources reported on this?)
        frequency_score = len(cluster_articles)
        
        # 2. Keyword Score (does this seem like breaking news?)
        keyword_count = sum(cluster_articles['title'].str.lower().str.contains(key).sum() for key in HIGHLIGHT_KEYWORDS)
        keyword_score = keyword_count * 5 # Give more weight to keywords
        
        total_score = frequency_score + keyword_score
        
        # --- Create Highlight Object ---
        # Use the first article in the cluster as the representative
        representative_article = cluster_articles.iloc[0]
        
        highlights.append({
            'title': representative_article['title'],
            'summary': representative_article['summary'],
            'category': representative_article['category'],
            'sources': list(cluster_articles['source'].unique()),
            'frequency': frequency_score,
            'score': total_score,
            'cluster_id': cluster_id
        })
        
    # Sort highlights by score in descending order
    sorted_highlights = sorted(highlights, key=lambda x: x['score'], reverse=True)
    return sorted_highlights

# --- MAIN EXECUTION ---
def main():
    """Runs the full AI processing and highlighting pipeline."""
    df = load_data(INPUT_FILE)
    df = categorize_articles(df)
    df = generate_and_cluster_articles(df)
    
    top_highlights = generate_highlights(df)
    
    print("\n--- 🏆 TOP 5 NEWS HIGHLIGHTS 🏆 ---\n")
    for i, highlight in enumerate(top_highlights[:5]):
        print(f"{i+1}. {highlight['title']}")
        print(f"   Category: {highlight['category']} | Score: {highlight['score']}")
        print(f"   Frequency: {highlight['frequency']} | Sources: {highlight['sources']}")
        print("-" * 20)

if __name__ == "__main__":
    main()