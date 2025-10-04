# in tests/test_chatbot.py
import sys
from pathlib import Path
import pytest
from langchain_core.documents import Document
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langchain_core.output_parsers import StrOutputParser

# Add the project root to the path to allow imports from 'services'
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from services.chatbot import prompt, llm, format_docs

def test_chatbot_with_context():
    """
    Tests the RAG chain's generation logic directly by building a temporary
    chain with a mock retriever function.
    """
    # 1. Define a mock retriever function for this test
    def mock_retriever(query: str):
        return [
            Document(
                page_content="The new CEO of TechCorp is officially Jane Smith.",
                metadata={}
            )
        ]

    # 2. Build the RAG chain, wrapping the mock function in RunnableLambda
    test_rag_chain = (
        {"context": RunnableLambda(mock_retriever) | format_docs, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )
    
    answer = test_rag_chain.invoke("Who is the new CEO of TechCorp?")
    
    assert "jane smith" in answer.lower()
    assert "don't have enough information" not in answer.lower()

def test_chatbot_without_context():
    """
    Tests the RAG chain's logic when no context is found.
    """
    def mock_retriever_empty(query: str):
        return []

    test_rag_chain = (
        {"context": RunnableLambda(mock_retriever_empty) | format_docs, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )

    answer = test_rag_chain.invoke("What is the weather like?")
    
    assert "don't have enough information" in answer.lower()