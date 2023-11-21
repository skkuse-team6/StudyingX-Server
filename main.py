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
        upload_dir = "uploads"
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
async def pdf_summary(input_data):
    try:
        #Load File
        pdf_file = input_data["file-id"]
        
        if (os.path.splitext(pdf_file)[1]=='.pdf'):
            loader = PyPDFLoader(pdf_file)
            document = loader.load()
        else:
            return -1

        #Split Document
        text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(chunk_size=1000, chunk_overlap=0)
        docs = text_splitter.split_documents(document)
        script = [Document(page_content=x) for x in text_splitter.split_text(input_data["script"])]

        #Save Vector
        index = VectorstoreIndexCreator(
                vectorstore_cls=FAISS,
                embedding=OpenAIEmbeddings(openai_api_key=os.environ["OPENAI_API_KEY"]),
                ).from_documents(docs)
        index.vectorstore.save_local(os.path.splitext(pdf_file)[0])
        index = VectorstoreIndexCreator(
                vectorstore_cls=FAISS,
                embedding=OpenAIEmbeddings(openai_api_key=os.environ["OPENAI_API_KEY"]),
                ).from_documents(script)
        index.vectorstore.save_local(os.path.splitext(pdf_file)[0]+'_script')

        #PDF QA
        chat = ChatOpenAI(model_name='gpt-4', temperature=0.9, openai_api_key=os.environ["OPENAI_API_KEY"])
        fdb = FAISS.load_local(os.path.splitext(pdf_file)[0], OpenAIEmbeddings(openai_api_key=os.environ["OPENAI_API_KEY"]))
        retriever = fdb.as_retriever(search_type='similarity', search_kwargs={"k":2})
        qa = RetrievalQA.from_chain_type(llm=chat,
                                        chain_type="stuff", retriever=retriever)
        
        outline = qa.run('Make an outline of this document').split('\n')
        # print(outline)

        #Script QA
        fdb = FAISS.load_local(os.path.splitext(pdf_file)[0]+'_script', OpenAIEmbeddings(openai_api_key=os.environ["OPENAI_API_KEY"]))
        retriever = fdb.as_retriever(search_type='similarity', search_kwargs={"k":2})
        qa = RetrievalQA.from_chain_type(llm=chat, chain_type="stuff", retriever=retriever)
        
        return_text = ''
        for subject in outline:
            if subject == '':
                continue
            return_text += subject + '\n'
            prompt = "Find suitable content from the provided document and summarize it into a single paragraph that will go under the heading \'" + subject + "\'. If you don't know the answer, just return '0'."
            # print("-----------------------------------------------------")
            # print(prompt)
            answer = qa.run(prompt)
            if answer == '0':
                continue
            # print(answer)
            return_text += answer + '\n\n'
        
        # print(return_text)
        return {"text": return_text}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
    # uvicorn main:app --host 0.0.0.0 --port 8000 --reload
