import requests
import openai


server_url = "http://localhost:8000/transcribe"

# file_mp3 = open("./audio_samples/hospital.mp3", "rb")
# audio_file_mp3 = {"file": ("hospital.mp3", file_mp3, "audio/mp3")}

file_wav = open("./audio_samples/sample1.wav", "rb")
audio_file_wav = {"file": ("sample1.wav", file_wav, "audio/wav")}

try:
    # response = requests.post(server_url, files=audio_file_mp3)
    response = requests.post(server_url, files=audio_file_wav)

    if response.status_code == 200:
        result = response.json()
        print("음성 인식 결과:", result["text"])
    else:
        print("오류 발생:", response.status_code, response.text)
except Exception as e:
    print("오류 발생:", str(e))
