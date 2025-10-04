import sys
from pathlib import Path
import pytest

# Add the project root to the path to allow imports from 'scripts'
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts.process_data import clean_author_field

@pytest.mark.parametrize("input_str, expected_output", [
    ("['John Doe', 'Jane Smith']", ['John Doe', 'Jane Smith']),
    ("['Single Author']", ['Single Author']),
    ("Just a String", ["Just a String"]),
    (None, []),
    ("['Malformed, list'", ["['Malformed, list'"]),
])
def test_clean_author_field(input_str, expected_output):
    """Tests the author field cleaning function with various inputs."""
    assert clean_author_field(input_str) == expected_output