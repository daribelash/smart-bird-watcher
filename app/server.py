from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import os, json

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

STATIC_DIR = os.path.join(os.path.dirname(__file__), "..", "static")
PREDICTION_FILE = os.path.join(STATIC_DIR, "latest_prediction.json")

app.mount("/images", StaticFiles(directory=STATIC_DIR), name="images")

class Prediction(BaseModel):
    species: str
    confidence: float
    image_filename: str

@app.post("/predict")
def update_prediction(pred: Prediction):
    with open(PREDICTION_FILE, "w") as f:
        json.dump(pred.dict(), f)
    return {"status": "success"}

@app.get("/predict/latest")
def get_latest_prediction():
    if os.path.exists(PREDICTION_FILE):
        with open(PREDICTION_FILE) as f:
            return json.load(f)
    return {"error": "No prediction available"}