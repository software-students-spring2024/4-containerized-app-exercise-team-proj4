
from unittest.mock import patch
import json
import tempfile
import pytest

import io
from app import app, audio_collection
from pymongo import MongoClient
from bson.objectid import ObjectId
import tempfile
#from io import BytesIO
#import speech_recognition as sr
#from app import transcribe_audio
#from unittest.mock import MagicMock


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
    """
    Test class for testing the client functionality.
    """
    def test_sanity_check(self):
        """
        Sanity check
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

    def test_delete_transcription(self, mocker, client):
        mocker.patch('app.audio_collection.delete_one').return_value.deleted_count = 1
        transcription_id = "61012f72421d474a9e65d0d0"
        response = client.delete(f'/delete_transcription/{transcription_id}')
        assert response.status_code == 200
        assert response.json == {"success": True}




    @patch('app.subprocess.run')
    def test_transcribe_audio_success(self, mock_run, mocker, client):
        mock_run.return_value.returncode = 0
        mocker.patch.object(audio_collection, 'insert_one').return_value.inserted_id = ObjectId("61012f72421d474a9e65d0d0")
        audio_content = b'Mock audio content'
        with tempfile.NamedTemporaryFile(suffix=".webm", delete=False) as tmpfile:
            tmpfile.write(audio_content)
        #issue with response
        response = client.post('/transcribe', data={'file': (open(tmpfile.name, 'rb'), 
                                            'mock_audio.webm')}, content_type='multipart/form-data')

        assert response.status_code == 200
        response_data = json.loads(response.data)
        assert "text" in response_data
        assert "id" in response_data

        transcription_id = response_data['id']
        assert audio_collection.find_one({"_id": ObjectId(transcription_id)}) is not None

if __name__ == "__main__":
    pytest.main()