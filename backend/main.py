from fastapi import FastAPI
from backend.routers import film

backend = FastAPI()

@backend.get("/")
def read_root():
    return {"message": "Hello, FastAPI!"}
 
# Mount routers
backend.include_router(film.router)
