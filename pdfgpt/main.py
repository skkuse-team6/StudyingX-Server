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

#Set os vairable To use the langchain library
os.environ["OPENAI_API_KEY"] = ""

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

@app.post("/Summary_gpt/")
async def pdf_summary(file: UploadFile, input_data: str):
    try:
        # file을 저장할 directory
        upload_dir = "uploads/pdf"
        os.makedirs(upload_dir, exist_ok=True)

        # save file
        with open(os.path.join(upload_dir, file.filename), "wb") as f:
            shutil.copyfileobj(file.file, f)

        # pdf file 읽기
        pdf = open(os.path.join(upload_dir, file.filename), "rb")

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

            query = input_data

            if query:
                #os 변수로 지정해서 해결하려했지만, similarity_search 부분이나 load_qa_chain에서 openai함수만을
                #인식하는 것 같습니다. 통일성이 조금 떨어질 부분인 것 같습니다.
                openai.api_key = ""
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
