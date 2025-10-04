# In tests/test_api.py
import pytest
import httpx
import os

# Get the hostname from an environment variable, defaulting to localhost
BACKEND_HOSTNAME = os.getenv("BACKEND_HOSTNAME", "127.0.0.1")
BASE_URL = f"http://{BACKEND_HOSTNAME}:8000"

@pytest.mark.integration
def test_highlights_endpoint():
    """Tests if the /highlights endpoint is reachable and returns a valid structure."""
    with httpx.Client() as client:
        response = client.get(f"{BASE_URL}/highlights")
        assert response.status_code == 200
        data = response.json()
        
        assert isinstance(data, dict) # The response should be a dictionary
        if data:
            first_value = next(iter(data.values()))
            assert isinstance(first_value, list)