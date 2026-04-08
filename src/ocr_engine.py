import cv2
import numpy as np
import re
from paddleocr import PaddleOCR

class PlateReader:
    """
    Handles Optical Character Recognition (OCR) for detected license plates using PaddleOCR.
    """
    def __init__(self):
        try:
            # Initialize PaddleOCR for English
            # use_angle_cls handles slightly tilted plates automatically
            # show_log=False prevents Paddle from spamming your terminal 
            self.reader = PaddleOCR(use_angle_cls=True, lang='en')
            print("PaddleOCR initialized successfully.")
        except Exception as e:
            print(f"Error initializing PaddleOCR: {e}")
            self.reader = None

    def preprocess(self, cropped_image):
        """
        Preprocesses the cropped plate image to enhance OCR accuracy.
        """
        try:
            # Convert to grayscale
            gray = cv2.cvtColor(cropped_image, cv2.COLOR_BGR2GRAY)
            
            # Apply bilateral filter to reduce noise while keeping edges sharp
            bfilter = cv2.bilateralFilter(gray, 11, 17, 17)
            
            # Apply adaptive thresholding
            thresh = cv2.adaptiveThreshold(
                bfilter, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                cv2.THRESH_BINARY, 11, 2
            )
            return thresh
        except Exception as e:
            print(f"Error during preprocessing: {e}")
            return cropped_image

    def clean_text(self, text):
        """
        Uses regex to strip out special characters and spaces.
        Returns only alphanumeric characters.
        """
        return re.sub(r'[^A-Za-z0-9]', '', text).upper()

    def read_text(self, cropped_image):
        """
        Runs the OCR engine on the raw image.
        Returns the cleaned text payload.
        """
        if self.reader is None:
            return ""

        try:
            # We skip manual preprocessing! Pass the raw cropped_image directly.
            # PaddleOCR handles lighting, noise, and channels internally.
            results = self.reader.ocr(cropped_image)
            
            # Handle cases where nothing is detected
            if not results or not results[0]:
                return ""

            # PaddleOCR returns a complex nested list: [ [ [box coords], ("Text", confidence_score) ] ]
            full_text = ""
            for line in results[0]:
                text_segment = line[1][0]  # Grab just the text string
                full_text += text_segment
            
            # Clean and return text
            cleaned = self.clean_text(full_text)
            return cleaned
            
        except Exception as e:
            print(f"Error during text reading: {e}")
            return ""