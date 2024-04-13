"""
Module-level docstring describing the purpose of the tests.
"""

import pytest
from app import app


@pytest.fixture
def clienttest():
    """
    Fixture to create a test client for the Flask application.
    """
    with app.test_client() as the_client:
        yield the_client


def test_index(client):
    """
    Test the index route of the Flask application.
    """
    response = client.get("/")
    assert response.status_code == 200


if __name__ == "__main__":
    pytest.main()
