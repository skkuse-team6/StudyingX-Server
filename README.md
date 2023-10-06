# StudyingX-Server

A user-friendly education tool utilizaing cutting-edge technologies to record and organize educators' speech and lecture content.

***

## Getting Started

To run the project, follow these steps:

### 1. Install Required Packages
First, install the necessary Python packages:

```
pip install fastapi uvicorn transformers requests
```

### 2. Optional Package Installation
If needed, you can also install the Transformers and datasets
packages:

```
pip install transformers==4.11.3 datasets==1.14.0
```

### 3. Configure STT API Key
To use the Speech-To-Text (STT) functionality, you'll need to configure your STT API key.
(Actually, I've already shared the API key on Slack as a text file. You just need to assign the received API key to the following part in the main.py file.)

```
openai.api_key = ""
```

### 4. Run the Server
Use the following command to run the FastAPI server:

```
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### 5. Access API Documentation
Once the server is running, you can access the API documentation at the following URL:
[FastAPI Swagger](http://localhost:8000/docs)

***

## Features

- Speech-To-Text Conversion
- PDF Summarization
