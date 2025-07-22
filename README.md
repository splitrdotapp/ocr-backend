# Receipt OCR Backend

A FastAPI backend service that processes receipt images using OCR and extracts structured data using AI.

## Features

- **OCR Processing**: Uses Google Cloud Vision API to extract text from receipt images
- **AI-Powered Parsing**: Uses Claude API to intelligently parse raw OCR text into structured data
- **REST API**: Simple POST endpoint for processing receipts
- **Structured Output**: Returns JSON with merchant info, transaction details, and line items
- **Error Handling**: Comprehensive error handling and validation

## Project Structure

```
receipt-ocr-backend/
├── main.py              # FastAPI application entry point
├── models.py            # Pydantic data models
├── ocr_service.py       # Google Cloud Vision OCR service
├── receipt_parser.py    # Claude API receipt parsing service
├── config.py           # Configuration settings
├── requirements.txt    # Python dependencies
└── README.md          # This file
```

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Google Cloud Vision Setup

1. Create a Google Cloud project
2. Enable the Vision API
3. Create a service account and download the JSON key file
4. Set the environment variable:

```bash
export GOOGLE_APPLICATION_CREDENTIALS="path/to/your/service-account-key.json"
```

### 3. Environment Variables (Optional)

```bash
export API_HOST="0.0.0.0"
export API_PORT="8000"
export LOG_LEVEL="INFO"
export MAX_FILE_SIZE="10485760"  # 10MB
```

## Usage

### Start the Server

```bash
python main.py
```

Or using uvicorn directly:

```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

### API Endpoints

#### POST /process-receipt

Process a receipt image and extract structured data.

**Request:**
- Method: POST
- Content-Type: multipart/form-data
- Body: Image file (JPEG, PNG, etc.)

**Example using curl:**

```bash
curl -X POST "http://localhost:8000/process-receipt" \
     -F "file=@receipt.jpg"
```

**Response:**

```json
{
  "merchant": {
    "name": "Sample Store",
    "address": "123 Main St, City, State 12345",
    "phone": "(555) 123-4567"
  },
  "transaction": {
    "date": "2024-01-15",
    "time": "14:30",
    "subtotal": 25.50,
    "tax": 2.04,
    "total": 27.54,
    "payment_method": "Credit Card"
  },
  "items": [
    {
      "description": "Milk 1 Gallon",
      "quantity": 1,
      "unit_price": 3.99,
      "total_price": 3.99
    },
    {
      "description": "Bread Loaf",
      "quantity": 2,
      "unit_price": 2.50,
      "total_price": 5.00
    }
  ],
  "raw_text": "Original OCR text..."
}
```

#### GET /health

Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "service": "Receipt OCR API"
}
```

### API Documentation

Once the server is running, you can access the interactive API documentation:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Error Handling

The API returns appropriate HTTP status codes:

- `200`: Success
- `400`: Bad request (invalid file type, empty file)
- `422`: Unprocessable entity (no text extracted from image)
- `500`: Internal server error

## Notes

- The service requires both Google Cloud Vision API and Claude API to be available
- Claude API calls are made without authentication (handled by the backend)
- Maximum file size is 10MB by default
- Supported image formats: JPEG, PNG, GIF, BMP, WebP
- The `raw_text` field in the response contains the original OCR output for debugging

## Development

To modify the parsing logic, edit `receipt_parser.py`. The prompt sent to Claude can be customized in the `_create_parsing_prompt` method.

To change the data structure, modify the Pydantic models in `models.py`.