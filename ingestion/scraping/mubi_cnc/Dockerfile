FROM python:3.12-slim

WORKDIR /app

COPY . /app

RUN pip install --no-cache-dir -r ingestion/scraping/mubi_cnc/requirements.txt

ENTRYPOINT ["python3", "ingestion/scraping/mubi_cnc/main.py"]
