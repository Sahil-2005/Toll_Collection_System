# import cv2
# import os

# from detector import LicensePlateDetector
# from ocr_engine import PlateReader
# from db_manager import TollDatabase

# def main():
#     # Initialize the core components
#     detector = LicensePlateDetector(model_path="../models/best.pt")
#     ocr_engine = PlateReader()
#     db_manager = TollDatabase(db_path="../database/toll_data.db")

#     # Open video feed
#     video_path = "data/test_video.mp4"
#     cap = cv2.VideoCapture(video_path)
    
#     if not cap.isOpened():
#         print(f"Error: Unable to open video source {video_path}")
#         return

#     print("Starting video processing... Press 'q' to quit.")

#     while True:
#         ret, frame = cap.read()
#         if not ret:
#             print("Video stream ended or error reading frame.")
#             break

#         # Detect license plates
#         detections = detector.detect(frame)

#         for det in detections:
#             x1, y1, x2, y2 = det['coords']
#             cropped_plate = det['crop']

#             # Read plate text
#             plate_text = ocr_engine.read_text(cropped_plate)

#             if plate_text:
#                 # Process toll transaction
#                 transaction = db_manager.process_toll(plate_text, toll_amount=50.0)
#                 status = transaction['status']
#                 msg = transaction['msg']

#                 # Setup colors based on status
#                 if status == "Success":
#                     color = (0, 255, 0)      # Green
#                 elif status == "Failed":
#                     color = (0, 0, 255)      # Red
#                 else:
#                     color = (0, 165, 255)    # Orange for Error/Unregistered

#                 # Draw bounding box and text
#                 cv2.rectangle(frame, (x1, y1), (x2, y2), color, 3)
#                 label = f"{plate_text} - {msg}"
                
#                 # Position text above the box
#                 text_y = y1 - 10 if y1 - 10 > 10 else y1 + 20
#                 cv2.putText(
#                     frame, label, (x1, text_y), 
#                     cv2.FONT_HERSHEY_SIMPLEX, 
#                     0.8, color, 2, cv2.LINE_AA
#                 )

#         # Show live video
#         cv2.imshow("Barrier-Free Toll Collection", frame)

#         # Break loop if 'q' is pressed
#         if cv2.waitKey(1) & 0xFF == ord('q'):
#             break

#     # Clean up
#     cap.release()
#     cv2.destroyAllWindows()

# if __name__ == "__main__":
#     main()


import cv2
import os

from detector import LicensePlateDetector
from ocr_engine import PlateReader
from db_manager import TollDatabase

def main():
    # Initialize the core components
    detector = LicensePlateDetector(model_path="../models/license-plate-finetune-v1m.pt")
    ocr_engine = PlateReader()
    db_manager = TollDatabase(db_path="../database/toll_data.db")

    # Define the input path (Can be a .jpg, .png, or .mp4)
    # Change this to your file name
    # input_path = "../data/test.jpg" 
    input_path = "../data/test_video.mp4" 
    # input_path = "../../test/images/000812dcf304a8e7_jpg.rf.ba32e6c184b3d974abcced6f7c29af6d.jpg" 
    # input_path = "../data/test_video.mp4" 
    
    # Check if input is an image or video
    ext = os.path.splitext(input_path)[1].lower()
    is_image = ext in ['.jpg', '.jpeg', '.png', '.bmp']

    if is_image:
        # Load single frame from image
        frame = cv2.imread(input_path)
        if frame is None:
            print(f"Error: Unable to open image {input_path}")
            return
        # We wrap it in a list so we can use the same loop as video
        frames = [frame]
    else:
        # Open video feed
        cap = cv2.VideoCapture(input_path)
        if not cap.isOpened():
            print(f"Error: Unable to open video source {input_path}")
            return
        frames = None # Video uses cap.read()

    print(f"Processing {input_path}... Press 'q' to quit.")

    while True:
        if is_image:
            if not frames: break # End after the single image is processed
            frame = frames.pop()
        else:
            ret, frame = cap.read()
            if not ret:
                print("Video stream ended.")
                break

        # --- Detection & OCR Logic (Stays exactly the same) ---
        detections = detector.detect(frame)

        for det in detections:
            x1, y1, x2, y2 = det['coords']
            cropped_plate = det['crop']

            plate_text = ocr_engine.read_text(cropped_plate)

            if plate_text:
                transaction = db_manager.process_toll(plate_text, toll_amount=50.0)
                status = transaction['status']
                msg = transaction['msg']

                color = (0, 255, 0) if status == "Success" else (0, 0, 255) if status == "Failed" else (0, 165, 255)

                cv2.rectangle(frame, (x1, y1), (x2, y2), color, 3)
                label = f"{plate_text} - {msg}"
                text_y = y1 - 10 if y1 - 10 > 10 else y1 + 20
                cv2.putText(frame, label, (x1, text_y), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2, cv2.LINE_AA)

        # Show output
        cv2.imshow("Barrier-Free Toll Collection", frame)

        # For images, wait indefinitely until a key is pressed
        # For videos, wait 1ms and continue
        wait_time = 0 if is_image else 1
        if cv2.waitKey(wait_time) & 0xFF == ord('q'):
            break

    # Clean up
    if not is_image:
        cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()