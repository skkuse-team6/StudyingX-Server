import requests
import openai


server_url = "http://localhost:8000/transcribe_whisper"

# file_mp3 = open("./audio_samples/광화문자생한방병원_1.mp3", "rb")
# audio_file_mp3 = {"file": ("광화문자생한방병원_1.mp3", file_mp3, "audio/mp3")}

file_wav = open("./audio_samples/샘플_1.wav", "rb")
audio_file_wav = {"file": ("샘플_1.wav", file_wav, "audio/wav")}

try:
    # response = requests.post(server_url, files=audio_file_mp3)
    response = requests.post(server_url, files=audio_file_wav)

    if response.status_code == 200:
        result = response.json()
        print(result); print()
        print("음성 인식 결과:", result['text'])
    else:
        print("오류 발생:", response.status_code, response.text)
except Exception as e:
    print("오류 발생:", str(e))