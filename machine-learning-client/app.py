"""
Machine Learning Client for Speech to Text Processing
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import speech_recognition as sr
import pymongo
import os
import subprocess
import tempfile
from bson.objectid import ObjectId
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DATABASE_NAME")
mongo_client = pymongo.MongoClient(MONGO_URI)
db = mongo_client[DB_NAME]
audio_collection = db["audio_data"]


@app.route("/transcribe", methods=["POST"])
def transcribe_audio():
    """
    Transcribe uploaded audio file to text
    """
    if "file" not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    with tempfile.NamedTemporaryFile(suffix=".webm", delete=False) as tmpfile:
        file.save(tmpfile.name)
        wav_filename = f"{tmpfile.name}.wav"
        subprocess.run(["ffmpeg", "-i", tmpfile.name, wav_filename])

    try:
        recognizer = sr.Recognizer()
        with sr.AudioFile(wav_filename) as source:
            audio_data = recognizer.record(source)
            text = recognizer.recognize_google(audio_data)

            audio_doc_id = audio_collection.insert_one({"text": text}).inserted_id
            response = jsonify({"text": text, "id": str(audio_doc_id)}), 200
    except sr.UnknownValueError:
        response = (
            jsonify({"error": "Google Speech Recognition could not understand audio"}),
            500,
        )
    except sr.RequestError as e:
        response = (
            jsonify(
                {
                    "error": f"Could not request results from Google Speech Recognition service; {e}"
                }
            ),
            500,
        )
    finally:
        os.remove(wav_filename)
        os.remove(tmpfile.name)

    return response


@app.route("/transcriptions", methods=["GET"])
def get_transcriptions():
    """
    Get all transcribed texts
    """
    transcriptions = list(audio_collection.find({}, {"text": 1}))
    for transcription in transcriptions:
        transcription["_id"] = str(transcription["_id"])
    return jsonify(transcriptions), 200


@app.route("/delete_transcription/<id>", methods=["DELETE"])
def delete_transcription(id):
    """
    Delete a transcribed text by ID
    """
    result = audio_collection.delete_one({"_id": ObjectId(id)})
    if result.deleted_count:
        return jsonify({"success": True}), 200
    return jsonify({"error": "Not found"}), 404


if __name__ == "__main__":
    app.run(debug=True, port=3001)
