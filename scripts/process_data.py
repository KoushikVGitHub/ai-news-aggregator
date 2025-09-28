import pandas as pd
from pathlib import Path
import ast # Used to safely evaluate string-formatted lists

def standardize_newsdata(df):
    """Standardizes the DataFrame from newsdata_raw.csv, including UI fields."""
    df = df.rename(columns={
        'title': 'title',
        'description': 'summary',
        'link': 'article_url',
        'source_id': 'source',
        'pubDate': 'published_date',
        'image_url': 'image_url',   # Add image_url
        'creator': 'authors'       # Add creator as authors
    })
    
    # Use the summary (which comes from the description) as the full_text
    df['full_text'] = df['summary'] 

    required_cols = ['title', 'summary', 'article_url', 'source', 'published_date', 'image_url', 'authors', 'full_text']
    
    # Ensure all required columns exist, filling missing ones with None
    for col in required_cols:
        if col not in df.columns:
            df[col] = None
            
    return df[required_cols]

def standardize_worldnews(df):
    """Standardizes the DataFrame from worldnews_raw.csv, including UI fields."""
    df = df.rename(columns={
        'title': 'title',
        'summary': 'summary', # Using 'text' as summary for now, will also map to full_text
        'url': 'article_url',
        'source_country': 'source',
        'publish_date': 'published_date',
        'image': 'image_url',       # Add image as image_url
        'authors': 'authors',       # Keep authors
        'text': 'full_text'         # Add text as full_text'
    })
    
    required_cols = ['title', 'summary', 'article_url', 'source', 'published_date', 'image_url', 'authors', 'full_text']
    
    for col in required_cols:
        if col not in df.columns:
            df[col] = None
            
    return df[required_cols]

def clean_author_field(authors_str):
    """Safely converts a string representation of a list into a Python list."""
    if pd.isna(authors_str):
        return []
    try:
        authors_list = ast.literal_eval(authors_str)
        if isinstance(authors_list, list):
            return authors_list
    except (ValueError, SyntaxError):
        return [authors_str]
    return []

def main():
    """Main function to run the data processing pipeline."""
    data_dir = Path("../data")
    newsdata_path = data_dir / "newsdata_raw.csv"
    worldnews_path = data_dir / "worldnews_raw.csv"
    output_path = data_dir / "cleaned_news.csv"

    print("Step 1: Loading raw data files...")
    df_newsdata = pd.read_csv(newsdata_path)
    df_worldnews = pd.read_csv(worldnews_path)

    print("Step 2: Standardizing data formats...")
    df_newsdata_std = standardize_newsdata(df_newsdata)
    df_worldnews_std = standardize_worldnews(df_worldnews)

    list_of_records = df_newsdata_std.to_dict('records') + df_worldnews_std.to_dict('records')

    print("Step 3: Combining and cleaning data...")
    df_combined = pd.DataFrame(list_of_records)

    # --- Data Cleaning for all columns ---
    df_combined.dropna(subset=['title', 'article_url'], inplace=True)
    df_combined.dropna(subset=['summary'], inplace=True)
    df_combined['published_date'] = pd.to_datetime(df_combined['published_date'], errors='coerce')
    df_combined.dropna(subset=['published_date'], inplace=True)
    df_combined.drop_duplicates(subset=['article_url'], keep='first', inplace=True)

    # Clean new UI-specific fields
    #df_combined['summary'] = df_combined['summary'].apply(lambda x: str(x) if pd.notna(x) else "")
    df_combined['full_text'] = df_combined['full_text'].apply(lambda x: str(x) if pd.notna(x) else "")
    df_combined['image_url'] = df_combined['image_url'].apply(lambda x: str(x) if pd.notna(x) else "")
    df_combined['authors'] = df_combined['authors'].apply(clean_author_field)

    print(f"Cleaning complete. Total articles: {len(df_combined)}")

    print(f"Step 4: Saving cleaned data to {output_path}...")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df_combined.to_csv(output_path, index=False, encoding='utf-8')
    print("Done.")

if __name__ == "__main__":
    main()