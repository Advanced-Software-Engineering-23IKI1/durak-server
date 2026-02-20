FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt . 
COPY src ./src
COPY tests ./tests

RUN python3 -m pip install -r requirements.txt
CMD ["python3", "src/main.py"]
