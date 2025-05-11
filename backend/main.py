import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.routers import film, festival, metabase

backend = FastAPI()

allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")

backend.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@backend.get("/")
def read_root():
    return {"message": "Hello, FastAPI!"}
 
# Mount routers
backend.include_router(film.router)
backend.include_router(festival.router)
backend.include_router(metabase.router)

for route in backend.routes:
    print(f"{route.path} -> {route.name}")
