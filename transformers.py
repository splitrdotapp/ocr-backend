import json
from typing import Dict, Any
from decimal import Decimal
from models import ReceiptData, ErrorResponse, LineItem, MerchantInfo, TransactionInfo, Response
from datetime import datetime   

def receipt_data_to_json(receipt_data: ReceiptData) -> str:
    """
    Convert ReceiptData object to JSON string by manually mapping all fields.
    
    Args:
        receipt_data (ReceiptData): The receipt data object to convert
        
    Returns:
        str: JSON string representation of the receipt data
    """
    data_dict = receipt_data_to_dict(receipt_data)
    return json.dumps(data_dict, ensure_ascii=False)

def receipt_data_to_dict(receipt_data: ReceiptData) -> Dict[str, Any]:
    """
    Convert ReceiptData object to dictionary by manually mapping all fields.
    
    Args:
        receipt_data (ReceiptData): The receipt data object to convert
        
    Returns:
        Dict[str, Any]: Dictionary representation of the receipt data
    """
    # Map merchant info
    merchant_dict = {
        "name": receipt_data.merchant.name,
        "address": receipt_data.merchant.address,
        "phone": receipt_data.merchant.phone
    }
    
    # Map transaction info
    transaction_dict = {
        "date": receipt_data.transaction.date,
        "time": receipt_data.transaction.time,
        "subtotal": float(receipt_data.transaction.subtotal) if receipt_data.transaction.subtotal is not None else None,
        "tax": float(receipt_data.transaction.tax) if receipt_data.transaction.tax is not None else None,
        "total": float(receipt_data.transaction.total),
        "payment_method": receipt_data.transaction.payment_method
    }
    
    # Map line items
    items_list = []
    for item in receipt_data.items:
        item_dict = {
            "description": item.description,
            "quantity": item.quantity,
            "unit_price": float(item.unit_price) if item.unit_price is not None else None,
            "total_price": float(item.total_price)
        }
        items_list.append(item_dict)
    
    # Combine all data
    result = {
        "merchant": merchant_dict,
        "transaction": transaction_dict,
        "items": items_list,
        "raw_text": receipt_data.raw_text
    }
    
    return result

def receipt_data_to_json_with_formatting(receipt_data: ReceiptData, indent: int = 2) -> str:
    """
    Convert ReceiptData object to formatted JSON string with custom indentation.
    
    Args:
        receipt_data (ReceiptData): The receipt data object to convert
        indent (int): Number of spaces for indentation (default: 2)
        
    Returns:
        str: Formatted JSON string representation of the receipt data
    """
    data_dict = receipt_data_to_dict(receipt_data)
    return json.dumps(data_dict, indent=indent, ensure_ascii=False)

def create_success_response(receipt_data: ReceiptData, status_code: int = 200) -> Response:
    """
    Create a complete success response payload with receipt data.
    
    Args:
        receipt_data (ReceiptData): The receipt data object to include
        status_code (int): HTTP status code (default: 200)
        
    Returns:
        Dict[str, Any]: Complete response payload with metadata
    """
    return {
        "status": "success",
        "status_code": status_code,
        "data": receipt_data_to_dict(receipt_data),
        "timestamp": datetime.now().isoformat()
    }

def create_error_response(error: ErrorResponse, status_code: int = 400) -> Dict[str, Any]:
    """
    Create a complete error response payload by manually mapping error fields.
    
    Args:
        error (ErrorResponse): The error object to include
        status_code (int): HTTP status code (default: 400)
        
    Returns:
        Dict[str, Any]: Complete error response payload
    """
    error_dict = {
        "detail": error.detail,
        "error_code": error.error_code
    }
    
    return {
        "status": "error",
        "status_code": status_code,
        "error": error_dict,
        "timestamp": datetime.now().isoformat()
    }

# Example usage:
if __name__ == "__main__":
    # Create sample data
    merchant = MerchantInfo(
        name="Sample Store",
        address="123 Main St, City, State 12345",
        phone="555-123-4567"
    )
    
    transaction = TransactionInfo(
        date="2024-01-15",
        time="14:30:00",
        subtotal=Decimal("25.98"),
        tax=Decimal("2.08"),
        total=Decimal("28.06"),
        payment_method="Credit Card"
    )
    
    items = [
        LineItem(
            description="Coffee Beans",
            quantity=2,
            unit_price=Decimal("8.99"),
            total_price=Decimal("17.98")
        ),
        LineItem(
            description="Milk",
            quantity=1,
            unit_price=Decimal("3.50"),
            total_price=Decimal("3.50")
        ),
        LineItem(
            description="Pastry",
            quantity=1,
            unit_price=Decimal("4.50"),
            total_price=Decimal("4.50")
        )
    ]
    
    receipt = ReceiptData(
        merchant=merchant,
        transaction=transaction,
        items=items,
        raw_text="Sample OCR text..."
    )
    
    # Convert to JSON (various methods)
    print("Simple JSON conversion:")
    print(receipt_data_to_json(receipt))
    
    print("\nFormatted JSON conversion:")
    print(receipt_data_to_json_with_formatting(receipt))
    
    print("\nComplete success response:")
    success_response = create_success_response(receipt)
    print(json.dumps(success_response, indent=2))