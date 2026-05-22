FROM python:3.12-slim

WORKDIR /app

COPY . /app

RUN pip install --no-cache-dir -r ingestion/scraping/allocine/requirements.txt

ENTRYPOINT ["python3", "ingestion/scraping/allocine/main.py"]
