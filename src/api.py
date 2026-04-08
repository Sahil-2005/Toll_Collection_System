import os

import cv2
import numpy as np
from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from src.db_manager import TollDatabase
from src.detector import LicensePlateDetector
from src.ocr_engine import PlateReader

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# MODEL_PATH = os.path.join(BASE_DIR, "models", "best.pt")
MODEL_PATH = os.path.join(BASE_DIR, "models", "license-plate-finetune-v1m.pt")
DB_PATH = os.path.join(BASE_DIR, "database", "toll_data.db")

app = FastAPI(title="ALPR Toll API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


detector = LicensePlateDetector(model_path=MODEL_PATH)
plate_reader = PlateReader()
db = TollDatabase(db_path=DB_PATH)


@app.get("/api/health")
def health_check():
    return {"status": "ok"}


@app.get("/api/users")
def get_users():
    users = db.get_all_users()
    return {"count": len(users), "users": users}


@app.get("/api/users/{plate_number}")
def get_user_by_plate(plate_number: str):
    user = db.get_user_by_plate(plate_number)
    if not user:
        return {"found": False, "user": None}
    return {"found": True, "user": user}


@app.post("/api/process-image")
async def process_image(file: UploadFile = File(...)):
    file_bytes = await file.read()
    np_arr = np.frombuffer(file_bytes, np.uint8)
    image = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

    if image is None:
        return {
            "plate_text": None,
            "status": "Error",
            "message": "Invalid image file",
            "updated_balance": None,
            "bbox": None,
        }

    detections = detector.detect(image)
    if not detections:
        return {
            "plate_text": None,
            "status": "Error",
            "message": "No plate detected",
            "updated_balance": None,
            "bbox": None,
        }

    plate_text = ""
    selected_bbox = None
    for detection in detections:
        crop = detection.get("crop")
        coords = detection.get("coords")
        if crop is None or crop.size == 0:
            continue

        plate_text = plate_reader.read_text(crop)
        if plate_text:
            selected_bbox = coords
            break

    if not plate_text:
        return {
            "plate_text": None,
            "status": "Error",
            "message": "Plate detected but text extraction failed",
            "updated_balance": None,
            "bbox": None,
        }

    transaction = db.process_toll(plate_text)
    user = db.get_user_by_plate(plate_text)
    return {
        "plate_text": plate_text,
        "status": transaction.get("status", "Error"),
        "message": transaction.get("message") or transaction.get("msg", "Unknown"),
        "updated_balance": transaction.get("updated_balance"),
        "bbox": selected_bbox,
        "user": user,
    }
