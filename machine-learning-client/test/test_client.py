import os
import tempfile
import pytest
import json
import io
from app import app
from pymongo import MongoClient
from bson.objectid import ObjectId


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

@pytest.fixture
def test_app():
    app.config['MONGO_URI'] = 'mongodb://localhost:3000/mydatabase'
    client = MongoClient()
    db = client.mydatabase
    app.audio_collection = db.audio_data
    yield app

class TestClient:
    def test_sanity_check(self):
        """
        Test debugging... making sure that we can run a simple test that always passes.
        Note the use of the example_fixture in the parameter list - any setup and teardown in that fixture will be run before and after this test function executes
        From the main project directory, run the `python3 -m pytest` command to run all tests.
        """
        expected = True 
        actual = True  
        assert actual == expected, "Expected True to be equal to True!"


    def post(self, url, data=None):
        return self.app.post(url, data=data)

    def test_get_transcriptions(self, client, test_app):
        response = client.get("/transcriptions")
        assert response.status_code == 200
        response_data = json.loads(response.data)
        assert isinstance(response_data, list)

    
    def test_delete_transcriptions_error(self, client):
        non_existent_id = ObjectId()
        response = client.delete(f"/delete_transcription/{non_existent_id}")
        assert response.status_code == 404
        assert response.json == {"error": "Not found"}
    
    def test_transcribe_audio_no_file(self, client):
        response = client.post("/transcribe")
        assert response.status_code == 400
        assert response.json == {"error": "No file part"}

    def test_transcribe_audio_empty_file(self, client):
        data = {"file": (io.BytesIO(b""), "")}
        response = client.post("/transcribe", data=data)
        assert response.status_code == 400
        assert response.json == {"error": "No selected file"}
    
   
    
if __name__ == "__main__":
    pytest.main()