from fastapi import FastAPI
from fastapi.testclient import TestClient
import main
from main import app

client = TestClient(app)

def test_upload_file():
    file_path = "./endpoint_test_files/audio_sample.mp3"
    response = client.post(
        "/upload_file/",
        files={"file": ("filename", open(file_path, "rb"), "audio/mp3")}
        )
    file_id = response.json()["file_id"]
    assert response.status_code == 200
    assert response.json() == {"message": "File uploaded successfully", "file_id": file_id}

def test_Speech_to_Text():
    file_path = "./endpoint_test_files/audio_sample.mp3"
    with open(file_path, "rb") as audio_file:
        files = {"file": ("audio_sample.mp3", audio_file, "audio/mp3")}
        response = client.post("/Speech-to-Text/", files=files)

    assert response.status_code == 200
    assert response.json()["text"] is not None

def test_PDF_Summary():
    file_id = "handbook.pdf"
    script = "dd"
    model = "gpt-3.5-turbo"
    response = client.post(
        "/PDF_Summary/",
        params={'file_id': file_id, 'script': script, 'model_gpt': model}
    )

    assert response.status_code == 200

'''가상환경에서 pytest command: python3 -m pytest'''
