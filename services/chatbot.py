import os
from dotenv import load_dotenv
from pymongo import MongoClient
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_mongodb import MongoDBAtlasVectorSearch
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

# --- INITIALIZATION ---
load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if not MONGO_URI or not GOOGLE_API_KEY:
    raise ValueError("Missing MONGO_URI or GOOGLE_API_KEY in .env file")

# 1. Initialize MongoDB Connection
client = MongoClient(MONGO_URI)
db = client.news_db
collection = db.articles

# 2. Initialize the Embedding Model (must be the same as in the generation script)
# This model runs locally and is used to convert the user's question into a vector.
embedding_model = HuggingFaceEmbeddings(model_name='all-MiniLM-L6-v2')

# 3. Initialize the Vector Store
vector_store = MongoDBAtlasVectorSearch(
    collection=collection,
    embedding=embedding_model,
    index_name="vector_index",
    text_key="summary",    # The field in your documents that was embedded
    embedding_key="embedding" # The field where the embedding vector is stored
)
# 4. Initialize the Retriever
# This component finds the most relevant articles in the database.
retriever = vector_store.as_retriever(search_kwargs={'k': 5})

# 5. Initialize the Generative Model (Gemini)
llm = ChatGoogleGenerativeAI(model="gemini-flash-latest", temperature=0.5)

# 6. Define the RAG Prompt Template
template = """
Answer the following question based ONLY on the context provided.
If the context does not contain the answer, say "I don't have enough information to answer that."

CONTEXT:
{context}

QUESTION:
{question}
"""
prompt = ChatPromptTemplate.from_template(template)

# --- RAG CHAIN ---
def format_docs(docs):
    """Helper function to format retrieved documents for the prompt."""
    return "\n\n".join(f"Title: {doc.page_content}" for doc in docs)

# The full chain that takes a question, retrieves context, formats the prompt, calls the LLM, and parses the output.
rag_chain = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)

def ask_question(question: str):
    """Invokes the RAG chain to answer a user's question."""
    if not question:
        return "Please ask a question."
    return rag_chain.invoke(question)