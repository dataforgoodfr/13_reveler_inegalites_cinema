import os
import psycopg

ENV = os.getenv("ENV", "development")
SQL_FILE_PATH = "database/data/sample/sample.sql"

# Safety check: never run this in production
if ENV.lower() == "production":
    raise RuntimeError("❌ This script cannot be run in production.")

# Load SQL script
with open(SQL_FILE_PATH, "r") as f:
    sql_script = f.read()

# Database connection settings (from environment variables or hardcoded for dev)
DB_NAME = os.getenv("POSTGRES_DB", "ric_db")
DB_USER = os.getenv("POSTGRES_USER", "postgres")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD", "postgres")
DB_HOST = os.getenv("POSTGRES_HOST", "db")
DB_PORT = os.getenv("POSTGRES_PORT", "5432")

# Connect and execute
try:
    conn = psycopg.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT,
    )
    conn.autocommit = True  # important for executing multiple statements
    with conn.cursor() as cur:
        cur.execute(sql_script)
    print("✅ SQL script executed successfully.")
except Exception as e:
    print(f"❌ Failed to execute script: {e}")
finally:
    if 'conn' in locals():
        conn.close()
