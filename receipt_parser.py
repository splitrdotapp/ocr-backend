import json
import logging
from typing import Dict, Any, Optional
from models import ReceiptData, MerchantInfo, TransactionInfo, LineItem
from decimal import Decimal
import re
import aiohttp
import os
from dotenv import load_dotenv

logger = logging.getLogger(__name__)
load_dotenv()  # Load environment variables from .env file

class ReceiptParser:
    """Service for parsing raw OCR text into structured receipt data using OpenAI GPT"""
    
    def __init__(self):
        """Initialize the receipt parser"""
        self.api_url = "https://api.openai.com/v1/chat/completions"
        self.api_key = os.getenv("OPENAI_API_KEY", "YOUR_OPENAI_API_KEY_HERE")
        self.model = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")  # or "gpt-4", "gpt-4-turbo"
        
        if self.api_key == "YOUR_OPENAI_API_KEY_HERE" or not self.api_key:
            logger.warning("OpenAI API key not set. Please set OPENAI_API_KEY environment variable.")
        
    async def parse_receipt(self, raw_text: str) -> ReceiptData:
        """
        Parse raw OCR text into structured receipt data using OpenAI GPT
        
        Args:
            raw_text: Raw text extracted from receipt image
            
        Returns:
            ReceiptData: Structured receipt information
        """
        try:
            # Create prompt for GPT to parse the receipt
            prompt = self._create_parsing_prompt(raw_text)
            
            # Call OpenAI API
            parsed_data = await self._call_openai_api(prompt)
            
            # Convert to ReceiptData model
            receipt_data = self._convert_to_receipt_data(parsed_data, raw_text)
            
            return receipt_data
            
        except Exception as e:
            logger.error(f"Error parsing receipt: {e}")
            raise Exception(f"Receipt parsing failed: {str(e)}")
    
    def _create_parsing_prompt(self, raw_text: str) -> str:
        """Create a prompt for GPT to parse the receipt"""
        return f"""
        You are an expert at parsing receipt data. Please analyze the following raw OCR text from a receipt and extract structured information.

        Raw OCR Text:
        {raw_text}

        Please extract and return ONLY a valid JSON object with the following structure. Do not include any other text, explanations, or formatting:

        {{
            "merchant": {{
                "name": "Store Name",
                "address": "Store Address if available",
                "phone": "Phone number if available"
            }},
            "transaction": {{
                "date": "Transaction date if available (YYYY-MM-DD format)",
                "time": "Transaction time if available (HH:MM format)",
                "subtotal": 0.00,
                "tax": 0.00,
                "total": 0.00,
                "payment_method": "Payment method if available"
            }},
            "items": [
                {{
                    "description": "Item description",
                    "quantity": 1,
                    "unit_price": 0.00,
                    "total_price": 0.00
                }}
            ]
        }}

        Important guidelines:
        - Extract all line items with their descriptions and prices
        - Use null for missing information rather than empty strings
        - Ensure all prices are numeric values (not strings)
        - If quantity is not specified, assume 1
        - Be as accurate as possible with item descriptions
        - Total should match the final amount paid
        - Look for common receipt patterns like subtotal, tax, and total lines
        - Identify the merchant name, usually at the top of the receipt
        - Extract date and time from timestamp information
        - Your response must be valid JSON only, no other text or formatting

        RESPOND ONLY WITH VALID JSON. NO OTHER TEXT.
        """
    
    async def _call_openai_api(self, prompt: str) -> Dict[str, Any]:
        """Call OpenAI API to parse the receipt"""
        try:
            if self.api_key == "YOUR_OPENAI_API_KEY_HERE" or not self.api_key:
                raise Exception("OpenAI API key not configured. Please set OPENAI_API_KEY environment variable.")
            
            payload = {
                "model": self.model,
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a receipt parsing expert. You must respond only with valid JSON data, no explanations or additional text."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "max_tokens": 2000,
                "temperature": 0.1,  # Low temperature for consistent, factual responses
                "response_format": {"type": "json_object"}  # Force JSON response (GPT-4 Turbo feature)
            }
            
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.api_url,
                    headers=headers,
                    json=payload
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        logger.error(f"OpenAI API error: {response.status} - {error_text}")
                        raise Exception(f"OpenAI API error: {response.status} - {error_text}")
                    
                    response_data = await response.json()
                    
                    # Extract the text content from OpenAI's response
                    if "choices" not in response_data or len(response_data["choices"]) == 0:
                        raise Exception("No response from OpenAI API")
                    
                    gpt_text = response_data["choices"][0]["message"]["content"]
                    
                    # Clean up the response (remove any markdown formatting)
                    cleaned_text = re.sub(r'```json\n?', '', gpt_text)
                    cleaned_text = re.sub(r'```\n?', '', cleaned_text).strip()
                    
                    # Parse JSON
                    parsed_data = json.loads(cleaned_text)
                    
                    logger.info("Successfully parsed receipt using OpenAI GPT")
                    return parsed_data
                    
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse GPT's JSON response: {e}")
            logger.error(f"Raw response: {gpt_text}")
            raise Exception("Failed to parse receipt data from GPT response")
        except Exception as e:
            logger.error(f"OpenAI API call failed: {e}")
            raise
    
    def _convert_to_receipt_data(self, parsed_data: Dict[str, Any], raw_text: str) -> ReceiptData:
        """Convert parsed data dictionary to ReceiptData model"""
        try:
            # Extract merchant info
            merchant_data = parsed_data.get("merchant", {})
            merchant = MerchantInfo(
                name=merchant_data.get("name", "Unknown Store"),
                address=merchant_data.get("address"),
                phone=merchant_data.get("phone")
            )
            
            # Extract transaction info
            transaction_data = parsed_data.get("transaction", {})
            transaction = TransactionInfo(
                date=transaction_data.get("date"),
                time=transaction_data.get("time"),
                subtotal=self._safe_decimal(transaction_data.get("subtotal")),
                tax=self._safe_decimal(transaction_data.get("tax")),
                total=Decimal(str(transaction_data.get("total", 0))),
                payment_method=transaction_data.get("payment_method")
            )
            
            # Extract line items
            items_data = parsed_data.get("items", [])
            items = []
            
            for item_data in items_data:
                item = LineItem(
                    description=item_data.get("description", "Unknown Item"),
                    quantity=item_data.get("quantity"),
                    unit_price=self._safe_decimal(item_data.get("unit_price")),
                    total_price=Decimal(str(item_data.get("total_price", 0)))
                )
                items.append(item)
            
            # Create receipt data
            receipt_data = ReceiptData(
                merchant=merchant,
                transaction=transaction,
                items=items,
                raw_text=raw_text
            )
            
            return receipt_data
            
        except Exception as e:
            logger.error(f"Error converting parsed data to ReceiptData: {e}")
            raise Exception("Failed to convert parsed data to structured format")
    
    def _safe_decimal(self, value) -> Optional[Decimal]:
        """Safely convert a value to Decimal, returning None if conversion fails"""
        if value is None:
            return None
        try:
            return Decimal(str(value))
        except:
            return None
    
    def is_available(self) -> bool:
        """Check if the OpenAI API service is available"""
        return self.api_key and self.api_key != "YOUR_OPENAI_API_KEY_HERE"