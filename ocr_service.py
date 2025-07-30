import logging
import base64
import os
import aiohttp
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class OCRService:
    async def extract_text(self, image_content: bytes) -> str:
        """
        Extract text from an image using OpenAI's GPT-4o (receipt_parser.py style)
        """
        logger.info("Starting LLM-based OCR processing for image")

        api_url = "https://api.openai.com/v1/chat/completions"
        api_key = os.getenv("OPENAI_API_KEY")
        model = os.getenv("OPENAI_MODEL", "gpt-4o")

        if not api_key:
            logger.error("OpenAI API key not set. Please set OPENAI_API_KEY environment variable.")
            raise Exception("OpenAI API key not configured.")

        try:
            image_base64 = base64.b64encode(image_content).decode('utf-8')
            logger.info("Image encoded to base64")

            payload = {
                "model": model,
                "messages": [
                    {
                        "role": "system",
                        "content": "You are an OCR assistant. Extract all readable text from the provided image."
                    },
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{image_base64}"
                                }
                            }
                        ]
                    }
                ],
                "max_tokens": 2000,
                "temperature": 0.1
            }

            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}"
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(api_url, headers=headers, json=payload) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        logger.error(f"OpenAI API error: {response.status} - {error_text}")
                        raise Exception(f"OpenAI API error: {response.status} - {error_text}")

                    response_data = await response.json()
                    if "choices" not in response_data or len(response_data["choices"]) == 0:
                        raise Exception("No response from OpenAI API")

                    extracted_text = response_data["choices"][0]["message"]["content"].strip()
                    logger.info("Successfully extracted text using LLM")
                    return extracted_text

        except Exception as e:
            logger.error(f"Error during LLM OCR processing: {e}")
            raise Exception(f"LLM OCR processing failed: {str(e)}")