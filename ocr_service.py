import easyocr
import numpy as np
from PIL import Image
import io
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class OCRService:
    """Service for extracting text from images using EasyOCR"""
    
    def __init__(self):
        """Initialize the EasyOCR reader"""
        try:
            # Initialize EasyOCR reader with English
            # You can add more languages: ['en', 'es', 'fr', etc.]
            self.reader = easyocr.Reader(['en'], gpu=False)  # Set gpu=True if you have CUDA
            logger.info("EasyOCR reader initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize EasyOCR reader: {e}")
            raise Exception(f"OCR initialization failed: {str(e)}")
    
    async def extract_text(self, image_content: bytes) -> str:
        """
        Extract text from an image using EasyOCR
        
        Args:
            image_content: Raw image bytes
            
        Returns:
            str: Extracted text from the image
        """
        logger.info("Starting OCR processing for image")

        try:
            # Convert bytes to PIL Image
            logger.info("Decoding image bytes to PIL Image")
            image = Image.open(io.BytesIO(image_content))
            logger.info("Image successfully decoded")
            
            # Convert PIL Image to numpy array
            image_array = np.array(image)
            logger.info("Converted PIL Image to numpy array")
            
            # Perform OCR
            results = self.reader.readtext(image_array)
            logger.info(f"EasyOCR found {len(results)} text elements in the image")
            
            if not results:
                logger.warning("No text detected in the image")
                return ""
            
            # Extract text from results
            # EasyOCR returns list of tuples: (bbox, text, confidence)
            extracted_texts = []
            
            for (bbox, text, confidence) in results:
                # Only include text with reasonable confidence (> 0.3)
                if confidence > 0.3:
                    extracted_texts.append(text)
            
            # Join all text with newlines to preserve structure
            full_text = '\n'.join(extracted_texts)
            
            logger.info(f"Successfully extracted {len(full_text)} characters from image")
            logger.info(f"Found {len(extracted_texts)} text elements with confidence > 0.3")
            
            return full_text
            
        except Exception as e:
            logger.info(f"Error during OCR processing: {e}")
            raise Exception(f"OCR processing failed: {str(e)}")
    
    def is_available(self) -> bool:
        """Check if the OCR service is available"""
        try:
            return self.reader is not None
        except:
            return False