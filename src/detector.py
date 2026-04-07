import cv2
from ultralytics import YOLO

class LicensePlateDetector:
    """
    Handles detecting license plates in video frames using a YOLOv8 model.
    """
    def __init__(self, model_path="../models/best.pt"):
        try:
            # Load the YOLO model
            self.model = YOLO(model_path)
            print(f"YOLO model loaded successfully from {model_path}")
        except Exception as e:
            print(f"Error loading YOLO model: {e}")
            self.model = None

    def detect(self, frame):
        """
        Runs YOLO inference on the given frame to detect license plates.
        Returns a list of dicts with cropped images and bounding box coords.
        """
        if self.model is None:
            return []

        results = self.model(frame, verbose=False)
        detections = []
        
        # Parse inference results
        for r in results:
            boxes = r.boxes
            for box in boxes:
                # Get coordinates in [x1, y1, x2, y2] format
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                
                # Ensure coordinates are within frame boundaries
                h, w = frame.shape[:2]
                x1, y1 = max(0, x1), max(0, y1)
                x2, y2 = min(w, x2), min(h, y2)
                
                # Crop the license plate image
                cropped_img = frame[y1:y2, x1:x2]
                
                if cropped_img.size > 0:
                    detections.append({
                        "coords": [x1, y1, x2, y2],
                        "crop": cropped_img
                    })
        return detections
