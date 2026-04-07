import glob
import os
import random
import sqlite3

import cv2

from src.detector import LicensePlateDetector
from src.ocr_engine import PlateReader


def resolve_images_dir(script_dir):
    """Resolve the images directory with a few sensible fallbacks."""
    candidates = [
        os.path.join(script_dir, "data", "images"),
        os.path.join(script_dir, "images"),
        os.path.join(script_dir, "..", "images"),
    ]

    for path in candidates:
        normalized = os.path.abspath(path)
        if os.path.isdir(normalized):
            return normalized
    return None


def resolve_model_path(script_dir):
    """Resolve YOLO model path so detector can be initialized from project root."""
    candidates = [
        os.path.join(script_dir, "models", "best.pt"),
        os.path.join(script_dir, "..", "models", "best.pt"),
    ]

    for path in candidates:
        normalized = os.path.abspath(path)
        if os.path.isfile(normalized):
            return normalized

    # Fall back to detector default behavior if model isn't found in known locations.
    return "../models/best.pt"


def collect_images(images_dir, limit=150):
    """Collect up to `limit` images from the given folder."""
    patterns = ["*.jpg", "*.jpeg", "*.png", "*.bmp", "*.webp"]
    image_paths = []

    for pattern in patterns:
        image_paths.extend(glob.glob(os.path.join(images_dir, pattern)))

    image_paths = sorted(image_paths)
    return image_paths[:limit]


def initialize_database(db_path):
    """Create database and registered_vehicles table if it doesn't exist."""
    os.makedirs(os.path.dirname(db_path), exist_ok=True)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS registered_vehicles (
            plate_number TEXT PRIMARY KEY,
            owner_name TEXT,
            wallet_balance REAL,
            is_active BOOLEAN
        )
        """
    )
    conn.commit()
    return conn


def extract_first_plate_text(image, detector, plate_reader):
    """Run detector + OCR and return first non-empty plate text found."""
    detections = detector.detect(image)

    for det in detections:
        cropped_plate = det.get("crop")
        if cropped_plate is None or cropped_plate.size == 0:
            continue

        plate_text = plate_reader.read_text(cropped_plate)
        if plate_text:
            return plate_text

    return ""


def seed_database():
    script_dir = os.path.dirname(os.path.abspath(__file__))

    images_dir = resolve_images_dir(script_dir)
    if not images_dir:
        print("No images folder found. Checked: data/images, images, and ../images")
        return

    image_paths = collect_images(images_dir, limit=150)
    total_images = len(image_paths)

    if total_images == 0:
        print(f"No image files found in: {images_dir}")
        return

    db_path = os.path.abspath(os.path.join(script_dir, ".", "database", "toll_data.db"))
    conn = initialize_database(db_path)
    cursor = conn.cursor()

    model_path = resolve_model_path(script_dir)
    detector = LicensePlateDetector(model_path=model_path)
    plate_reader = PlateReader()

    inserted_count = 0

    for idx, image_path in enumerate(image_paths, start=1):
        print(f"[{idx}/{total_images}] Processing: {os.path.basename(image_path)}")

        image = cv2.imread(image_path)
        if image is None:
            print("  -> Skipped (unable to read image)")
            continue

        plate_text = extract_first_plate_text(image, detector, plate_reader)
        if not plate_text:
            print("  -> Skipped (no plate text extracted)")
            continue

        owner_name = f"User_{idx}"
        wallet_balance = round(random.uniform(100.0, 2000.0), 2)
        is_active = True

        cursor.execute(
            """
            INSERT OR IGNORE INTO registered_vehicles
            (plate_number, owner_name, wallet_balance, is_active)
            VALUES (?, ?, ?, ?)
            """,
            (plate_text, owner_name, wallet_balance, is_active),
        )

        if cursor.rowcount > 0:
            inserted_count += 1
            print(f"  -> Inserted plate: {plate_text}")
        else:
            print(f"  -> Ignored duplicate plate: {plate_text}")

    conn.commit()
    conn.close()

    print("\nSeeding complete.")
    print(f"Total images processed: {total_images}")
    print(f"Total new records inserted: {inserted_count}")
    print(f"Database path: {db_path}")


if __name__ == "__main__":
    seed_database()
