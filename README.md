# StudyingX-Server

A user-friendly education tool utilizaing cutting-edge technologies to record and organize educators' speech and lecture content.

---

## Getting Started

To run the project, follow these steps:

### 1. Setup Python Virtual Environment

If venv is not installed, install it with the following command:

```bash
sudo apt-get install python3-venv # Ubuntu
# brew install python3-venv # MacOS
```

Then, create a new virtual environment:

```bash
python3 -m venv venv
```

Activate the virtual environment:

```bash
. venv/bin/activate
```

### 2. Install Required Packages

Install the necessary Python packages.

```bash
pip install -r requirements.txt
```

> [!NOTE]
> If you want to update requirements.txt(adding or removing deps), use the following command:
>
> ```bash
> pip freeze > requirements.txt
> ```

> [!NOTE]
> To terminate virtual environment, use the following command:
>
> ```bash
> deactivate
> ```

### 3. Configure STT API Key

To use the Speech-To-Text (STT) functionality, you'll need to configure your STT API key.
~~(Actually, I've already shared the API key on Slack as a text file. You just need to assign the received API key to the following part in the main.py file.)~~

Create `.env` file in the root directory and add the following line.
Replace `<KEY>` with your API key.

```python
OPENAI_API_KEY=<KEY> # Your API key
```

### 4. Run the Server

Use the following command to run the FastAPI server:

```bash
python3 -m uvicorn main:app --reload
```

### 5. Access API Documentation

Once the server is running, you can access the API documentation at the following URL:
[FastAPI Swagger](http://localhost:8000/docs)

---

## Features

- Speech-To-Text Conversion
- PDF Summarization
