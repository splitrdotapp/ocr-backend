from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from models import ReceiptData, ErrorResponse
from ocr_service import OCRService
from receipt_parser import ReceiptParser
import logging
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
async def process_receipt(file: UploadFile = File(...)):
    """
    Process a receipt image and extract structured data.
    
    Args:
        file: Image file (JPEG, PNG, etc.)
        
    Returns:
        ReceiptData: Structured receipt information
    """
    try:
        # Validate file type
        if not file.content_type or not file.content_type.startswith('image/'):
            raise HTTPException(
                status_code=400,
                detail="File must be an image (JPEG, PNG, etc.)"
            )
        
        # Read file content
        file_content = await file.read()
        
        if len(file_content) == 0:
            raise HTTPException(
                status_code=400,
                detail="Empty file provided"
            )
        
        logger.info(f"Processing receipt image: {file.filename}")
        
        # Extract text using OCR
        raw_text = await ocr_service.extract_text(file_content)
        
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

if __name__ == "__main__":
    uvicorn.run(app, host=config.API_HOST, port=config.API_PORT)