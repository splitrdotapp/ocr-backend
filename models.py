from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from decimal import Decimal

class ImageRequest(BaseModel):
    """Request model for base64 encoded image"""
    image_base64: str = Field(..., description="Base64 encoded image data")

class LineItem(BaseModel):
    """Individual item on the receipt"""
    description: str = Field(..., description="Item description")
    quantity: Optional[int] = Field(None, description="Quantity purchased")
    unit_price: Optional[Decimal] = Field(None, description="Price per unit")
    total_price: Decimal = Field(..., description="Total price for this item")

class MerchantInfo(BaseModel):
    """Merchant/store information"""
    name: str = Field(..., description="Store/merchant name")
    address: Optional[str] = Field(None, description="Store address")
    phone: Optional[str] = Field(None, description="Store phone number")

class TransactionInfo(BaseModel):
    """Transaction details"""
    date: Optional[str] = Field(None, description="Transaction date")
    time: Optional[str] = Field(None, description="Transaction time")
    subtotal: Optional[Decimal] = Field(None, description="Subtotal before tax")
    tax: Optional[Decimal] = Field(None, description="Tax amount")
    total: Decimal = Field(..., description="Total amount")
    payment_method: Optional[str] = Field(None, description="Payment method used")

class ReceiptData(BaseModel):
    """Complete receipt data structure"""
    merchant: MerchantInfo
    transaction: TransactionInfo
    items: List[LineItem] = Field(..., description="List of items purchased")
    raw_text: Optional[str] = Field(None, description="Original OCR text for debugging")

class Response(BaseModel):
    """Success response model"""
    status: str = Field("success", description="Response status")
    status_code: int = Field(200, description="HTTP status code")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")
    data: ReceiptData = Field(..., description="Extracted receipt data")

class ErrorResponse(BaseModel):
    """Error response model"""
    detail: str
    error_code: Optional[str] = None