import cv2
import easyocr
import numpy as np
import re

class PlateReader:
    """
    Handles Optical Character Recognition (OCR) for detected license plates.
    """
    def __init__(self):
        try:
            # Initialize EasyOCR reader for English
            self.reader = easyocr.Reader(['en'], gpu=False) # Switch to True if GPU available
            print("EasyOCR reader initialized successfully.")
        except Exception as e:
            print(f"Error initializing EasyOCR: {e}")
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
            
            # Apply adaptive thresholding to make text pop
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
        Runs the OCR engine on the preprocessed image.
        Returns the cleaned text payload.
        """
        if self.reader is None:
            return ""

        processed_img = self.preprocess(cropped_image)
        try:
            # Do OCR
            results = self.reader.readtext(processed_img)
            
            # Combine all detected text blocks
            full_text = "".join([result[1] for result in results])
            
            # Clean and return text
            cleaned = self.clean_text(full_text)
            return cleaned
        except Exception as e:
            print(f"Error during text reading: {e}")
            return ""
