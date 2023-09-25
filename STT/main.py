from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
import shutil
import openai
import os

app = FastAPI()

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
        return FileResponse(file_path, headers={"Content-Disposition": f"attachment; filename={filename}"})

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/transcribe/")
async def transcribe_audio_file(file: UploadFile):
    try:
        # audio_file upload & read
        upload_dir = "uploads"
        os.makedirs(upload_dir, exist_ok=True)

        # save file
        with open(os.path.join(upload_dir, file.filename), "wb") as f:
            shutil.copyfileobj(file.file, f)

        content = open(os.path.join(upload_dir, file.filename), "rb")

        # STT 설정 및 호출
        openai.api_key = "비밀"
        transcript = openai.Audio.transcribe("whisper-1", content)

        # return {"text": transcript}
        return transcript

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
