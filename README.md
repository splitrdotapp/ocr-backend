# Receipt OCR Backend

A FastAPI backend service that processes receipt images using OCR and extracts structured data using AI.

## Features

- **OCR Processing**: Uses EasyOCR (completely free) to extract text from receipt images
- **AI-Powered Parsing**: Uses OpenAI GPT models to intelligently parse raw OCR text into structured data
- **REST API**: Simple POST endpoint for processing receipts
- **Structured Output**: Returns JSON with merchant info, transaction details, and line items
- **Error Handling**: Comprehensive error handling and validation
- **No Cloud Dependencies**: OCR runs completely offline (only OpenAI API requires internet)
- **Flexible Model Choice**: Supports GPT-3.5-turbo, GPT-4, or GPT-4-turbo

## Project Structure

```
receipt-ocr-backend/
├── main.py              # FastAPI application entry point
├── models.py            # Pydantic data models
├── ocr_service.py       # EasyOCR service
├── receipt_parser.py    # OpenAI GPT receipt parsing service
├── config.py           # Configuration settings
├── requirements.txt    # Python dependencies
└── README.md          # This file
```

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

**Note**: First installation of EasyOCR will download language models (~50MB for English).

### 2. OpenAI API Setup

1. Get your API key from [OpenAI Platform](https://platform.openai.com/api-keys)
2. Set the environment variable:

```bash
export OPENAI_API_KEY="your-openai-api-key-here"
```

### 3. Environment Variables (Optional)

```bash
export API_HOST="0.0.0.0"
export API_PORT="8000"
export LOG_LEVEL="INFO"
export OPENAI_API_KEY="your-openai-api-key-here"
export OPENAI_MODEL="gpt-3.5-turbo"    # Options: gpt-3.5-turbo, gpt-4, gpt-4-turbo
export OCR_LANGUAGES="en"              # Comma-separated: "en,es,fr"
export OCR_GPU="false"                 # Set to "true" if you have CUDA GPU
export OCR_CONFIDENCE_THRESHOLD="0.3"  # Minimum confidence for text detection
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
- Content-Type: application/json
- Body: JSON with base64 encoded image

**Request Body:**
```json
{
  "image_base64": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQEAYABgAAD/2wBDAAM..."
}
```

**Example using curl:**

```bash
curl -X POST "http://localhost:8000/process-receipt" \
     -H "Content-Type: application/json" \
     -d '{
       "image_base64": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQEAYABgAAD/2wBDAAM..."
     }'
```

**Example using Python:**

```python
import base64
import requests

# Read and encode image
with open("receipt.jpg", "rb") as image_file:
    base64_string = base64.b64encode(image_file.read()).decode()

# Make API request
response = requests.post(
    "http://localhost:8000/process-receipt",
    json={"image_base64": base64_string}
)

print(response.json())
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

- **Completely Free OCR**: Uses EasyOCR which runs locally with no API costs
- **OpenAI API Required**: You need an OpenAI API key for receipt parsing
- **Model Options**: Supports GPT-3.5-turbo (cheaper, fast) or GPT-4 (more accurate, slower)
- **First Run**: EasyOCR will download language models on first use (~50MB for English)
- **GPU Support**: Set `OCR_GPU=true` if you have CUDA GPU for faster processing
- **Languages**: Supports 80+ languages - modify `OCR_LANGUAGES` environment variable
- **Offline OCR**: OCR works completely offline (only OpenAI API requires internet)
- Images should be sent as base64 encoded strings in JSON requests
- The API accepts base64 data with or without data URL prefixes
- Supported image formats: JPEG, PNG, GIF, BMP, WebP
- The `raw_text` field in the response contains the original OCR output for debugging

## OpenAI API Costs

- **GPT-3.5-turbo**: ~$0.001 per receipt (very affordable)
- **GPT-4**: ~$0.03 per receipt (more expensive but better accuracy)
- **GPT-4-turbo**: ~$0.01 per receipt (good balance of cost/performance)

## Performance Notes

- **CPU Processing**: Without GPU, processing takes 2-5 seconds per image
- **GPU Processing**: With CUDA GPU, processing takes 0.5-1 seconds per image
- **Memory Usage**: Requires ~1GB RAM for the EasyOCR models
- **Accuracy**: Very good for printed text, decent for handwritten text

## Development

To modify the parsing logic, edit `receipt_parser.py`. The prompt sent to Claude can be customized in the `_create_parsing_prompt` method.

To change the data structure, modify the Pydantic models in `models.py`.