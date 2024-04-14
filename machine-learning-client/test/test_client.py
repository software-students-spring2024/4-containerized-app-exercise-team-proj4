"""
test function class for ML client
"""
from io import BytesIO
import io
from unittest.mock import patch, MagicMock, mock_open
import json
import pytest
from bson import ObjectId
from app import app, audio_collection

# pylint: disable=W0621,E1101,R1732, C0116, W0107, W0613, R0913


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


def mock_remove(filename):
    """
    Mock function to replace os.remove, only accepts parameters, does not perform any action.
    """
    pass


@pytest.fixture
def mock_audio_recognizer():
    """Fixture to mock speech_recognition Recognizer and AudioFile."""
    with patch("speech_recognition.AudioFile", MagicMock()) as mock_audio_file:
        with patch("speech_recognition.Recognizer") as mock_recognizer:
            yield mock_audio_file, mock_recognizer


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

    @patch("subprocess.run")
    @patch("tempfile.NamedTemporaryFile")
    @patch("os.remove")
    @patch("speech_recognition.AudioFile")
    @patch("speech_recognition.Recognizer")
    @patch("builtins.open", new_callable=mock_open)
    def test_transcribe_audio_success(
        self,
        mock_file_open,
        mock_recognizer,
        mock_audio_file,
        mock_remove,
        mock_tempfile,
        mock_run,
        client,
    ):
        """
        Test to ensure audio transcription is successful.
        """
        mock_run.return_value.returncode = 0
        mock_tempfile.return_value.__enter__.return_value.name = (
            "/fakepath/faketemp.webm"
        )

        recognizer_instance = MagicMock()
        recognizer_instance.recognize_google.return_value = "Recognized text"
        mock_recognizer.return_value = recognizer_instance
        mock_audio_file.return_value.__enter__.return_value = MagicMock()

        audio_content = b"Mock audio content"
        audio_file = BytesIO(audio_content)
        audio_file.name = "mock_audio.webm"

        mock_insert = MagicMock()
        mock_insert.return_value.inserted_id = ObjectId()
        audio_collection.insert_one = mock_insert

        response = client.post(
            "/transcribe",
            data={"file": (audio_file, "mock_audio.webm")},
            content_type="multipart/form-data",
        )

        assert response.status_code == 200
        response_data = response.get_json()
        assert response_data["text"] == "Recognized text"
        assert "id" in response_data
        assert mock_insert.called  # Ensure database insert was called
        assert mock_run.called  # Ensure subprocess.run was called
        # Ensure file open function was called to simulate file writing
        mock_file_open.assert_called()


if __name__ == "__main__":
    pytest.main()
