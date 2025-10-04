import os
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pymongo import MongoClient
from pydantic import BaseModel
from datetime import datetime, timedelta
from services.chatbot import ask_question

# --- INITIALIZATION ---
load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")

app = FastAPI(title="AI News Aggregator API")
client = MongoClient(MONGO_URI)
db = client.news_db
collection = db.articles

# Allow the frontend to communicate with this backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, restrict this to frontend's domain
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
    Finds top story clusters for EACH category from the last 24 hours.
    """
    categories = ["sports", "lifestyle", "music", "finance", "general news"]
    highlights = {category: [] for category in categories}
    
    pipeline = [
        {"$match": {"cluster_id": {"$ne": -1}}},        # 1. Filter for articles in a cluster
        {"$sort": {"published_date": -1}},              # 2. Sort by date to get the newest representative
        {
            "$group": {                                 # 3. Group by story to calculate frequency
                "_id": "$cluster_id",
                "frequency": {"$sum": 1},
                "representative_article": {"$first": "$$ROOT"},
            }
        },
        {
            "$setWindowFields": {                       # 4. Rank stories within each category
                "partitionBy": "$representative_article.category",
                "sortBy": {"frequency": -1},
                "output": {"rank_in_category": {"$rank": {}}},
            }
        },
        {"$match": {"rank_in_category": {"$lte": 10}}}, # 5. Keep only the top 10 from each category
    ]
    
    top_stories = list(collection.aggregate(pipeline))
    
    # --- Organize the stories into their categories for the frontend ---
    for story in top_stories:
        article = story['representative_article']
        category = article.get('category')
        
        if category in highlights:
            article['_id'] = str(article['_id'])
            for key, value in article.items():
                if isinstance(value, float) and value != value:
                    article[key] = None

            article['frequency'] = story['frequency']
            highlights[category].append(article)
        
    return highlights

@app.post("/chatbot/ask")
def handle_chat_query(request: ChatRequest):
    """Endpoint to handle chatbot questions."""
    question = request.question
    answer = ask_question(question)
    return {"answer": answer}