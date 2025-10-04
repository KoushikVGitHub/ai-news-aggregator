# AI-Powered Australian News Aggregator & Chatbot

This project is a full-stack application that extracts news from multiple Australian sources, uses AI to categorize and identify key stories, and presents them in an interactive web dashboard. It also features an AI chatbot, powered by Google's Gemini and Retrieval-Augmented Generation (RAG), that can answer questions about the day's news highlights.

## ✨ Features

* **Multi-Source Aggregation:** Fetches news from both **Newsdata.io** and **World News API** for broad coverage.
* **AI-Powered Categorization:** Automatically classifies articles into categories like Finance, Technology, and Sports using a zero-shot model.
* **Semantic Clustering:** Groups articles reporting on the same story, even with different headlines, to identify trending topics.
* **Highlight Generation:** Scores and ranks news stories based on frequency and keywords to surface the most important highlights.
* **RAG Chatbot:** A sophisticated chatbot that uses a vector database (MongoDB Atlas) and the Gemini API to answer user questions based *only* on the context of the fetched news.
* **Interactive UI:** A user-friendly dashboard built with Streamlit to display highlights, images, authors, and the full article text.

## 🛠️ Technology Stack

* **Backend:** Python, FastAPI
* **Frontend:** Streamlit
* **Database:** MongoDB Atlas (with Atlas Vector Search)
* **AI/ML:**
    * **LLM:** Google Gemini Pro
    * **Framework:** LangChain
    * **Models:** `sentence-transformers` for embeddings, `transformers` for classification.
* **Data Handling:** Pandas

## 📁 Project Structure

```
/ai-news-aggregator
├── data/
├── scripts/
├── services/
├── backend/
├── ui/
├── .env
├── .gitignore
├── README.md
└── requirements.txt
```

## ⚙️ Setup & Configuration

Follow these steps to set up and run the project locally.

### 1. Clone the Repository
```bash
git clone <your-repository-link>
cd ai-news-aggregator
```

### 2. Create a Python Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Set up MongoDB Atlas
1.  Create a free account and a new cluster on **MongoDB Atlas**.
2.  In your cluster, create a database named `news_db` and a collection named `articles`.
3.  **Create a Vector Search Index:** This is a crucial step.
    * In your `articles` collection, go to the **Search** tab.
    * Create a new **Atlas Vector Search Index** using the JSON editor.
    * Name the index `default` and use the following definition:
    ```json
    {
      "fields": [{
        "type": "vector",
        "path": "embedding",
        "numDimensions": 384,
        "similarity": "cosine"
      }]
    }
4.  Configure Network Access:
    In the left-hand menu, under "Security," click Network Access.
    Click "Add IP Address" and select "Allow Access from Anywhere" (0.0.0.0/0). This is necessary for the Docker container to connect.
    ```

### 5. Create the `.env` File
Create a file named `.env` in the project's root directory. Copy the contents of your API keys and database connection string into it.

```
# MongoDB
MONGO_URI="your_mongodb_atlas_connection_string"

# Google Gemini
GOOGLE_API_KEY="your_gemini_api_key_here"

# News APIs
NEWSDATA_API_KEY="your_newsdata_api_key_here"
WORLDNEWS_API_KEY="your_worldnews_api_key_here"
```

## 🚀 How to Run the Project

## Option A: Run with Docker (Recommended)

This is the easiest way to run the entire application.
1. Prerequisite: Install Docker Desktop and ensure it is running.

2. Important: In ui/dashboard.py, make sure the backend URL is set to the Docker service name:
```bash
   BACKEND_URL = "http://backend:8000"
```

3. Run the Data Pipeline: Before starting the application, you must populate your database. Run the scripts in order:
```bash
# 1. Fetch, clean and standardize the raw data
python scripts/1_fetch_data.py
python scripts/2_process_data.py

# 2. Add AI features (categories and embeddings)
python scripts/3_generate_ai_features.py

# 3. Load the final data into MongoDB
python scripts/4_load_to_mongodb.py
```

4. Build and Run with Docker Compose: From the project root directory, run:
```bash
   docker-compose up --build
```
The application will be available at http://localhost:8501

## Option B: Run Manually

If you prefer not to use Docker, follow these steps.

1. Create a Python Environment & Install Dependencies
```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
```

2. Important: In ui/dashboard.py, make sure the backend URL is set to your local address:
```bash
   BACKEND_URL = "[http://127.0.0.1:8000](http://127.0.0.1:8000)"
```

3. Run the Data Pipeline
Execute the following scripts in order to fetch, process, and load the data.
```bash
# 1. Fetch, clean and standardize the raw data
python scripts/1_fetch_data.py
python scripts/2_process_data.py

# 2. Add AI features (categories and embeddings)
python scripts/3_generate_ai_features.py

# 3. Load the final data into MongoDB
python scripts/4_load_to_mongodb.py
```

4. Launch the Application
   You need to run the backend and frontend in two separate terminals.

###Terminal 1: Start the Backend API
```bash
   uvicorn backend.main:app --reload
```

###Terminal 2: Start the Frontend UI
```bash
   streamlit run ui/dashboard.py
```
The application will be available at http://localhost:8501