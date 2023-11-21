from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
# need install for langchain
import pickle
from PyPDF2 import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.llms import OpenAI
from langchain.chains.question_answering import load_qa_chain
from langchain.callbacks import get_openai_callback
import shutil
import openai
import os
import uuid
from dotenv import load_dotenv
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
# need install for langchain
from langchain.schema.document import Document
from langchain.document_loaders import PyPDFLoader
from langchain.indexes import VectorstoreIndexCreator
from langchain.chains import RetrievalQA
from langchain.chat_models import ChatOpenAI

# load value in .env file
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

#Set os vairable To use the langchain library
os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY

app = FastAPI()

def save_uploaded_file(upload_dir: str, file: UploadFile):
    # 랜덤한 파일 이름 생성하는 부분
    extension = os.path.splitext(file.filename)[1]
    file_id = f"{uuid.uuid4()}{extension}"
    file_path = os.path.join(upload_dir, file_id)

    # 파일 저장하는 부분
    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    return file_id

@app.post("/upload_file/")
async def upload_file(file: UploadFile):
    try:
        # file을 저장할 directory
        upload_dir = "uploads/pdf"
        os.makedirs(upload_dir, exist_ok=True)

        file_id = save_uploaded_file(upload_dir, file)

        return {"message": "File uploaded successfully", "file_id": file_id}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/download_file/{file_id}")
async def download_file(file_id: str):
    try:
        # saved path
        file_path = os.path.join("uploads", file_id)

        # 파일이 존재하지 않으면 404 반환
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="File not found")

        # file download
        return FileResponse(file_path, headers={"Content-Disposition": f"attachment; filen_id={file_id}"})

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

##### file 삭제
@app.delete("/delete_file/{file_id}")
async def delete_file(file_id: str, upload_dir: str = "uploads"):
    try:
        file_path = os.path.join(upload_dir, file_id)

        if os.path.exists(file_path):
            os.remove(file_path)
            return {"message": "File deleted successfully"}
        else:
            raise HTTPException(status_code=404, detail="File not found")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

##### file 목록 읽기
def get_file_list(directory):
    try:
        files = os.listdir(directory)
        return {"files": files}
    except Exception as e:
        return {"error": str(e)}

@app.get("/get_file_list/")
async def list_files(directory: str = "uploads"):
    return get_file_list(directory)


@app.post("/Speech-to-Text/")
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

@app.post("/PDF_Summary/")
async def pdf_summary(file_id: str):
    try:
        #Load File
        upload_dir = "uploads/pdf"
        file_name = file_id + ".pdf"

        # pdf file 읽기
        pdf = open(os.path.join(upload_dir, file_name), "rb")

        # recognize the extension for pdfgpt
        #file_extension = os.path.splitext(file_name)[1].lower()
        #print(file_extension)

        if pdf is not None:
            pdf_reader = PdfReader(pdf)

            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text()

            # parameter for tuning
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200,
                length_function=len
            )

            chunks = text_splitter.split_text(text=text)
            # # embeddings
            store_name = pdf.name[:-4]

            if os.path.exists(f"{store_name}.pkl"):
                with open(f"{store_name}.pkl", "rb") as f:
                    VectorStore = pickle.load(f)
                # st.write('Embeddings Loaded from the Disk')s
            else:
                embeddings = OpenAIEmbeddings()
                VectorStore = FAISS.from_texts(chunks, embedding=embeddings)
                with open(f"{store_name}.pkl", "wb") as f:
                    pickle.dump(VectorStore, f)

            query = "Find suitable content from the provided document and summarize it into a single paragraph that will go under the heading. Please write in English"

            if query:
                #os 변수로 지정해서 해결하려했지만, similarity_search 부분이나 load_qa_chain에서 openai함수만을
                #인식하는 것 같습니다. 통일성이 조금 떨어질 부분인 것 같습니다.
                openai.api_key = OPENAI_API_KEY
                docs = VectorStore.similarity_search(query=query, k=3)

                llm = OpenAI()
                chain = load_qa_chain(llm=llm, chain_type="stuff")
                with get_openai_callback() as cb:
                    response = chain.run(input_documents=docs, question=query)


        # return {"text": mytext}
        return {"text": response}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
    # uvicorn main:app --host 0.0.0.0 --port 8000 --reload
