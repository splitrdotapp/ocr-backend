from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from models import ReceiptData, ErrorResponse, ImageRequest
from ocr_service import OCRService
from receipt_parser import ReceiptParser
import logging
import base64
from config import config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Receipt OCR API",
    description="API for extracting structured data from receipt images",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
ocr_service = OCRService()
receipt_parser = ReceiptParser()

@app.post("/process-receipt", response_model=ReceiptData)
async def process_receipt(request: ImageRequest):
    """
    Process a receipt image and extract structured data.
    
    Args:
        request: ImageRequest containing base64 encoded image
        
    Returns:
        ReceiptData: Structured receipt information
    """
    try:
        # Validate base64 string
        if not request.image_base64:
            raise HTTPException(
                status_code=400,
                detail="image_base64 field is required"
            )
        
        # Decode base64 image
        try:
            # Remove data URL prefix if present (e.g., "data:image/jpeg;base64,")
            base64_data = request.image_base64
            if ',' in base64_data:
                base64_data = base64_data.split(',')[1]
            
            image_bytes = base64.b64decode(base64_data)
        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid base64 image data: {str(e)}"
            )
        
        if len(image_bytes) == 0:
            raise HTTPException(
                status_code=400,
                detail="Decoded image is empty"
            )
        
        logger.info("Processing base64 encoded receipt image")
        
        # Extract text using OCR
        raw_text = await ocr_service.extract_text(image_bytes)
        
        if not raw_text.strip():
            raise HTTPException(
                status_code=422,
                detail="No text could be extracted from the image"
            )
        
        # Parse receipt data using LLM
        receipt_data = await receipt_parser.parse_receipt(raw_text)
        
        logger.info("Receipt processed successfully")
        return receipt_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing receipt: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error while processing receipt"
        )

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "Receipt OCR API"}

# if __name__ == "__main__":
#     uvicorn.run(app, host=config.API_HOST, port=config.API_PORT)