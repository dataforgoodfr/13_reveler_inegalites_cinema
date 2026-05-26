FROM python:3.12-slim

ARG PREFECT_VERSION=3.4.24

WORKDIR /app

RUN apt-get update && apt-get install -y cron \
    && pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir \
        "prefect==${PREFECT_VERSION}" \
        "dbt-core==1.11.7" \
        "dbt-postgres==1.10.0" \
        "sqlalchemy>=2.0" \
        "psycopg[binary]>=3.2" \
        "python-dotenv>=1.0" \
        "beautifulsoup4>=4.13" \
        "dateparser>=1.2" \
        "playwright>=1.51" \
    && rm -rf /var/lib/apt/lists/*

COPY . /app
COPY ingestion/prefect/cleanup_crontab /etc/cron.d/cleanup_crontab
RUN chmod 0644 /etc/cron.d/cleanup_crontab && crontab /etc/cron.d/cleanup_crontab

ENV PYTHONPATH=/app
ENV DBT_PROFILES_DIR=/app/ingestion/dbt/profiles

WORKDIR /app

CMD service cron start && prefect
