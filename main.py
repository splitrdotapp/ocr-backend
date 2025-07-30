from fastapi import FastAPI, HTTPException, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from models import ReceiptData, ErrorResponse, Response
from ocr_service import OCRService
from receipt_parser import ReceiptParser
import logging
from config import config
from transformers import create_success_response, create_error_response, receipt_data_to_json_with_formatting, receipt_data_to_dict

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

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

@app.post("/process-receipt", response_model=Response)
async def process_receipt(file: UploadFile = File(...)):
    """
    Process a receipt image and extract structured data.
    
    Args:
        file: UploadFile containing the receipt image
        
    Returns:
        ReceiptData: Structured receipt information
    """
    logger.info("Received request to process receipt image")
    try:
        # Validate file upload
        if not file:
            raise HTTPException(
                status_code=400,
                detail="No file uploaded"
            )
        
        # Check if file is an image
        if not file.content_type or not file.content_type.startswith('image/'):
            raise HTTPException(
                status_code=400,
                detail="File must be an image (JPEG, PNG, etc.)"
            )
        
        # Check file size (optional - adjust max size as needed)
        max_file_size = 10 * 1024 * 1024  # 10MB
        file_size = 0
        
        # Read file content
        try:
            image_bytes = await file.read()
            file_size = len(image_bytes)
            
            if file_size == 0:
                raise HTTPException(
                    status_code=400,
                    detail="Uploaded file is empty"
                )
            
            if file_size > max_file_size:
                raise HTTPException(
                    status_code=413,
                    detail=f"File size ({file_size} bytes) exceeds maximum allowed size ({max_file_size} bytes)"
                )
                
        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail=f"Error reading uploaded file: {str(e)}"
            )
        
        logger.info(f"Processing uploaded receipt image: {file.filename} ({file_size} bytes)")
        
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

        print(create_success_response(receipt_data))

        return create_success_response(receipt_data)
        
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