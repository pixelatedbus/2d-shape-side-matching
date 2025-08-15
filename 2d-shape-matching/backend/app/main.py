import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.api import endpoints
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

app = FastAPI(title="hakim API")

FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGES_DIR = Path(__file__).resolve().parents[1] / "images"
app.mount("/images", StaticFiles(directory=IMAGES_DIR), name="images")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"],
)


app.include_router(endpoints.router, prefix="/api")

@app.get("/")
def read_root():
    return {"message": "oioioi"}
