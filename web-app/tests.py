"""
Tests for the web application.
"""

import pytest
from app import app


@pytest.fixture
def client():
    """
    Fixture to create a test client for the Flask application.
    """
    with app.test_client() as client:
        yield client


def test_index(client):
    """
    Test the index route of the Flask application.
    """
    response = client.get("/")
    assert response.status_code == 200


if __name__ == "__main__":
    pytest.main()