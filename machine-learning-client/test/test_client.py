"""
test function class for ML client
"""
import os
from io import BytesIO
import io
from unittest.mock import patch, MagicMock
import json
import tempfile
import pytest
from bson import ObjectId
from app import app, audio_collection

# pylint: disable=W0621,E1101,R1732, C0116

@pytest.fixture
def client():
    """
    client fixture
    """
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


@pytest.fixture
def mock_run():
    """
    mock_run fixture
    """
    return MagicMock()

def mock_remove():
    pass

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
        """
        post
        """
        return self.app.post(url, data=data)

    def test_get_transcriptions(self, client):
        """
        test get transcriptions
        """
        response = client.get("/transcriptions")
        assert response.status_code == 200
        response_data = json.loads(response.data)
        assert isinstance(response_data, list)

    def test_delete_transcriptions_error(self, client):
        """
        test if error from delete transcriptions
        """
        non_existent_id = ObjectId()
        response = client.delete(f"/delete_transcription/{non_existent_id}")
        assert response.status_code == 404
        assert response.json == {"error": "Not found"}

    def test_transcribe_audio_no_file(self, client):
        """
        test if no file from transcribe audio
        """
        response = client.post("/transcribe")
        assert response.status_code == 400
        assert response.json == {"error": "No file part"}

    def test_transcribe_audio_empty_file(self, client):
        """
        test if empty file from transcribe audio
        """
        data = {"file": (io.BytesIO(b""), "")}
        response = client.post("/transcribe", data=data)
        assert response.status_code == 400
        assert response.json == {"error": "No selected file"}

    def test_delete_transcription(self, mocker, client):
        """
        test if delete file sucess
        """
        mocker.patch("app.audio_collection.delete_one").return_value.deleted_count = 1
        transcription_id = "61012f72421d474a9e65d0d0"
        response = client.delete(f"/delete_transcription/{transcription_id}")
        assert response.status_code == 200
        assert response.json == {"success": True}

    @patch("app.subprocess.run")
    def test_transcribe_audio_success(self,monkeypatch, mock_run, mocker, client):
        """
        test transcribe audio sucess
        """
        mock_run.return_value.returncode = 0
        mocker.patch.object(
            audio_collection, "insert_one"
        ).return_value.inserted_id = ObjectId("61012f72421d474a9e65d0d0")
        audio_content = b"Mock audio content"
        with tempfile.NamedTemporaryFile(suffix=".webm", delete=False) as tmpfile:
            tmpfile.write(audio_content)

        if not os.path.exists(tmpfile.name):
            pytest.skip("Temporary file does not exist. Skipping test.")


        # wav_filename = tmpfile.name + ".wav"
        # if not os.path.exists(wav_filename):
        #     pytest.skip("WAV file does not exist. Skipping test.")
        audio_file = BytesIO(audio_content)
        audio_file.name = "mock_audio.webm"

        monkeypatch.setattr(os, "remove", mock_remove)

        response = client.post(
            "/transcribe",
            data={"file": (audio_file, "mock_audio.webm")},
            content_type="multipart/form-data",
        )

        assert response.status_code == 200
        response_data = json.loads(response.data)
        assert "text" in response_data
        assert "id" in response_data

        transcription_id = response_data["id"]
        assert (
            audio_collection.find_one({"_id": ObjectId(transcription_id)}) is not None
        )


if __name__ == "__main__":
    pytest.main()
