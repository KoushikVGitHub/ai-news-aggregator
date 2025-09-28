import os
import requests
import pandas as pd
from dotenv import load_dotenv
from newsdataapi import NewsDataApiClient
from datetime import datetime, timedelta

# --- API Fetching Functions (with Pagination) ---

def get_raw_news_from_newsdata(min_results=100):
    """Fetches and returns raw articles from Newsdata.io, handling pagination."""
    print("Fetching raw news from Newsdata.io...")
    api_key = os.getenv("NEWSDATA_API_KEY")
    if not api_key: return []

    all_articles = []
    next_page_token = None
    try:
        api = NewsDataApiClient(apikey=api_key)
        # Loop until we have enough results or there are no more pages
        while len(all_articles) < min_results:
            response = api.latest_api(country='au', language='en', page=next_page_token)
            results = response.get('results', [])
            if not results:
                break # Stop if the API returns no more articles
            
            all_articles.extend(results)
            next_page_token = response.get('nextPage')

            if not next_page_token:
                break # Stop if there is no next page token
        
        return all_articles
    except Exception as e:
        print(f"Error fetching from Newsdata.io: {e}")
        return all_articles # Return what we have so far

def get_raw_news_from_worldnews(min_results=100):
    """Fetches and returns raw articles from World News API, handling pagination."""
    print("Fetching raw news from World News API...")
    api_key = os.getenv("WORLDNEWS_API_KEY")
    if not api_key: return []

    all_articles = []
    offset = 0
    try:
        # Loop until we have enough results or the API stops returning news
        while len(all_articles) < min_results:
            api_url = "https://api.worldnewsapi.com/search-news"
            headers = {'x-api-key': api_key}
            yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
            params = {
                'source-country': 'au', 'language': 'en', 'earliest-publish-date': yesterday,
                'sort': 'publish-time', 'sort-direction': 'DESC',
                'number': 100,  # Request the max number of results per page
                'offset': offset # The starting point for the results
            }
            
            response = requests.get(api_url, headers=headers, params=params)
            response.raise_for_status()
            data = response.json()
            news = data.get('news', [])
            
            if not news:
                break # Stop if the API returns no more articles
            
            all_articles.extend(news)
            offset += len(news) # Increase the offset by the number of articles received
            
            # Safety break if offset gets too large or results are fewer than requested
            if len(news) < 100:
                break

        return all_articles
    except requests.exceptions.RequestException as e:
        print(f"Error fetching from World News API: {e}")
        return all_articles # Return what we have so far

# --- Main Execution ---
if __name__ == "__main__":
    load_dotenv()

    print("Fetching and saving raw data to separate files...")
    
    newsdata_articles_raw = get_raw_news_from_newsdata(min_results=100)
    worldnews_articles_raw = get_raw_news_from_worldnews(min_results=100)

    if newsdata_articles_raw:
        df_newsdata = pd.DataFrame(newsdata_articles_raw)
        df_newsdata.to_csv("../data/newsdata_raw.csv", index=False, encoding='utf-8')
        print(f"Saved {len(df_newsdata)} raw articles to newsdata_raw.csv")

    if worldnews_articles_raw:
        df_worldnews = pd.DataFrame(worldnews_articles_raw)
        df_worldnews.to_csv("../data/worldnews_raw.csv", index=False, encoding='utf-8')
        print(f"Saved {len(df_worldnews)} raw articles to worldnews_raw.csv")
    
    total = len(newsdata_articles_raw) + len(worldnews_articles_raw)
    print(f"\nTotal articles fetched: {total}")