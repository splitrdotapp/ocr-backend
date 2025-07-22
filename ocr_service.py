from google.cloud import vision
import logging
from typing import Optional
import os

logger = logging.getLogger(__name__)

class OCRService:
    """Service for extracting text from images using Google Cloud Vision"""
    
    def __init__(self):
        """Initialize the Google Cloud Vision client"""
        try:
            # Initialize the Google Cloud Vision client
            # Make sure to set GOOGLE_APPLICATION_CREDENTIALS environment variable
            # or use Google Cloud SDK authentication
            self.client = vision.ImageAnnotatorClient()
            logger.info("Google Cloud Vision client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Google Cloud Vision client: {e}")
            raise
    
    async def extract_text(self, image_content: bytes) -> str:
        """
        Extract text from an image using Google Cloud Vision OCR
        
        Args:
            image_content: Raw image bytes
            
        Returns:
            str: Extracted text from the image
        """
        try:
            # Create a Vision API image object
            image = vision.Image(content=image_content)
            
            # Perform text detection
            response = self.client.text_detection(image=image)
            
            # Check for errors
            if response.error.message:
                raise Exception(f'Google Cloud Vision API error: {response.error.message}')
            
            # Extract the full text
            texts = response.text_annotations
            
            if not texts:
                logger.warning("No text detected in the image")
                return ""
            
            # The first annotation contains the full detected text
            full_text = texts[0].description
            
            logger.info(f"Successfully extracted {len(full_text)} characters from image")
            return full_text
            
        except Exception as e:
            logger.error(f"Error during OCR processing: {e}")
            raise Exception(f"OCR processing failed: {str(e)}")
    
    def is_available(self) -> bool:
        """Check if the OCR service is available"""
        try:
            # Simple test to see if we can create a client
            return self.client is not None
        except:
            return False