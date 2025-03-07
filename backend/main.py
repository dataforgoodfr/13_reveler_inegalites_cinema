from fastapi import FastAPI

backend = FastAPI()

@backend.get("/")
def read_root():
    return {"message": "Hello, FastAPI!"}
