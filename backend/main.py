import os
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pymongo import MongoClient
from pydantic import BaseModel
from datetime import datetime, timedelta

# Import the chatbot service we just created
from services.chatbot import ask_question

# --- INITIALIZATION ---
load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")

app = FastAPI(title="AI News Aggregator API")
client = MongoClient(MONGO_URI)
db = client.news_db
collection = db.articles

# Allow the frontend (running on a different port) to communicate with this backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, restrict this to your frontend's domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- MODELS ---
class ChatRequest(BaseModel):
    question: str

# --- API ENDPOINTS ---
@app.get("/highlights")
def get_highlights():
    """
    Finds top story clusters from the last 24 hours based on frequency.
    """
    twenty_four_hours_ago = datetime.now() - timedelta(hours=24)
    
    # MongoDB Aggregation Pipeline to find top clusters
    pipeline = [
        # 1. Filter for recent articles that are part of a cluster
        {
            "$match": {
                "published_date": {"$gte": twenty_four_hours_ago},
                "cluster_id": {"$ne": -1} # -1 are unique articles, not clusters
            }
        },
        # 2. Group by cluster_id to count frequency and gather data
        {
            "$group": {
                "_id": "$cluster_id",
                "frequency": {"$sum": 1},
                "representative_article": {"$first": "$$ROOT"}
            }
        },
        # 3. Sort by frequency (most reported stories first)
        {"$sort": {"frequency": -1}},
        # 4. Limit to the top 10 stories
        {"$limit": 10}
    ]
    
    top_stories = list(collection.aggregate(pipeline))
    
    # --- Prepare the final response ---
    highlights = {"Top Stories": []}
    for story in top_stories:
        article = story['representative_article']
        article['_id'] = str(article['_id']) # Convert ObjectId
        
        # Clean potential NaN values
        for key, value in article.items():
            if isinstance(value, float) and value != value:
                article[key] = None

        article['frequency'] = story['frequency'] # Add frequency to the article object
        highlights["Top Stories"].append(article)
        
    return highlights

@app.post("/chatbot/ask")
def handle_chat_query(request: ChatRequest):
    """Endpoint to handle chatbot questions."""
    question = request.question
    answer = ask_question(question)
    return {"answer": answer}