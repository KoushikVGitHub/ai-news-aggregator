# tests/test_api.py
import pytest
import httpx

BASE_URL = "http://127.0.0.1:8000"

@pytest.mark.integration
def test_highlights_endpoint():
    """Tests if the /highlights endpoint is reachable and returns valid data."""
    timeout = httpx.Timeout(30.0, connect=5.0)
    with httpx.Client(timeout=timeout) as client:
        response = client.get(f"{BASE_URL}/highlights")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert "finance" in data 

@pytest.mark.integration
def test_chatbot_endpoint():
    """Tests if the /chatbot/ask endpoint can process a request."""
    timeout = httpx.Timeout(30.0, connect=5.0)
    with httpx.Client(timeout=timeout) as client:
        response = client.post(
            f"{BASE_URL}/chatbot/ask",
            json={"question": "What is the latest news?"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "answer" in data
        assert isinstance(data["answer"], str)