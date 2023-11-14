FROM python:3.11-bullseye

ADD . /app
WORKDIR /app

RUN export DEBIAN_FRONTEND=noninteractive && \
    apt update && apt install -y build-essential

RUN pip install --upgrade pip setuptools wheel && \
    pip install -r requirements.txt

CMD ["python", "-m", "uvicorn", "main:app", "--host=0.0.0.0"]
