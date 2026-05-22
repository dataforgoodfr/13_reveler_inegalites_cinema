import os

from dotenv import load_dotenv
from sqlalchemy import MetaData, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Load DATABASE_URL from env variables
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
DATABASE_SCHEMA = os.getenv("DATABASE_SCHEMA", "public")

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(bind=engine)
Base = declarative_base(metadata=MetaData(schema=DATABASE_SCHEMA))


# Dependency to get a session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
