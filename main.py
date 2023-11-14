from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from dotenv import load_dotenv
import shutil
import openai
import os

app = FastAPI()

load_dotenv()  # Load .env file
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


@app.post("/upload/")
async def upload_audio_file(file: UploadFile):
    try:
        # file을 저장할 directory
        upload_dir = "uploads"
        os.makedirs(upload_dir, exist_ok=True)

        # save file
        with open(os.path.join(upload_dir, file.filename), "wb") as f:
            shutil.copyfileobj(file.file, f)

        return {"message": "File uploaded successfully"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/download/{filename}")
async def download_audio_file(filename: str):
    try:
        # saved path
        file_path = os.path.join("uploads", filename)

        # 파일이 존재하지 않으면 404 반환
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="File not found")

        # file download
        return FileResponse(
            file_path,
            headers={"Content-Disposition": f"attachment; filename={filename}"},
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/transcribe_whisper/")
async def transcribe_audio_file(file: UploadFile):
    try:
        # upload 디렉토리 생성 or path 설정
        upload_dir = "uploads/stt"
        os.makedirs(upload_dir, exist_ok=True)

        # audio file 저장
        with open(os.path.join(upload_dir, file.filename), "wb") as f:
            shutil.copyfileobj(file.file, f)

        # audio file 읽기
        content = open(os.path.join(upload_dir, file.filename), "rb")

        # STT 설정 및 호출
        openai.api_key = OPENAI_API_KEY
        transcript = openai.Audio.transcribe("whisper-1", content)

        # return {"text": transcript}
        return transcript

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/Summary_gpt/")
async def pdf_summary(file: UploadFile):
    try:
        # file을 저장할 directory
        upload_dir = "uploads/pdf"
        os.makedirs(upload_dir, exist_ok=True)

        # save file
        with open(os.path.join(upload_dir, file.filename), "wb") as f:
            shutil.copyfileobj(file.file, f)

        return {"message": "File uploaded successfully"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
    # uvicorn main:app
