import os
import pandas as pd
from pathlib import Path
from dotenv import load_dotenv
from pymongo import MongoClient, operations
from pymongo.errors import BulkWriteError

def main():
    """Main function to load enriched data into MongoDB."""
    # --- 1. Configuration and Connection ---
    print("Step 1: Loading configuration and connecting to MongoDB...")
    load_dotenv()
    mongo_uri = os.getenv("MONGO_URI")
    if not mongo_uri:
        raise ValueError("MONGO_URI not found in .env file.")

    client = MongoClient(mongo_uri)
    db = client.news_db
    collection = db.articles
    
    print("Successfully connected to MongoDB.")

    # --- 2. Load Enriched Data ---
    data_dir = Path("../data")
    input_path = data_dir / "enriched_news.pkl"
    print(f"Step 2: Loading enriched data from {input_path}...")
    df = pd.read_pickle(input_path)
    # Convert dataframe to a list of dictionaries for insertion
    records = df.to_dict('records')
    print(f"Loaded {len(records)} records.")

    # --- 3. Prepare and Execute Bulk Upsert ---
    print("Step 3: Preparing and executing bulk upsert operation...")
    # Using 'upsert=True' will insert a document if it doesn't exist,
    # or update it if it does, based on the 'article_url'.
    bulk_operations = [
        operations.UpdateOne(
            {"article_url": rec["article_url"]},
            {"$set": rec},
            upsert=True
        )
        for rec in records
    ]
    
    if not bulk_operations:
        print("No records to upsert.")
        return

    try:
        result = collection.bulk_write(bulk_operations)
        print("\nBulk write operation complete.")
        print(f"  - Documents inserted: {result.upserted_count}")
        print(f"  - Documents modified: {result.modified_count}")
    except BulkWriteError as bwe:
        print("\nAn error occurred during bulk write:")
        print(bwe.details)
    
    print("Data loading process finished.")

if __name__ == "__main__":
    main()