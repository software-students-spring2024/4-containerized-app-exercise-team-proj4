import pytest
from app import app


@pytest.fixture
def test_client():
    with app.test_client() as client:
        yield client


def test_index(test_client):
    """
    Test index route.
    """
    response = test_client.get("/")
    assert response.status_code == 200
    assert b"Hello, World!" in response.data  


if __name__ == "__main__":
    pytest.main()