FROM python:3.12-slim

WORKDIR /app

RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir \
        "prefect==3.4.24" \
        "dbt-core==1.11.7" \
        "dbt-postgres==1.10.0" \
        "sqlalchemy>=2.0" \
        "psycopg[binary]>=3.2" \
        "python-dotenv>=1.0" \
        "beautifulsoup4>=4.13" \
        "dateparser>=1.2" \
        "playwright>=1.51"

COPY . /app

ENV PYTHONPATH=/app
ENV DBT_PROFILES_DIR=/app/ingestion/dbt/profiles

WORKDIR /app

ENTRYPOINT ["prefect"]
