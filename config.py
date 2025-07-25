import os
from typing import Optional
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

class Config:
    """Application configuration"""
    
    # API Configuration
    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
    API_PORT: int = int(os.getenv("API_PORT", "8000"))
    
    # OpenAI Configuration
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "YOUR_OPENAI_API_KEY_HERE")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")  # or "gpt-4", "gpt-4-turbo"
    
    # OCR Configuration
    OCR_LANGUAGES: list = os.getenv("OCR_LANGUAGES", "en").split(",")
    OCR_GPU: bool = os.getenv("OCR_GPU", "false").lower() == "true"
    OCR_CONFIDENCE_THRESHOLD: float = float(os.getenv("OCR_CONFIDENCE_THRESHOLD", "0.3"))
    
    # File Upload Limits
    MAX_FILE_SIZE: int = int(os.getenv("MAX_FILE_SIZE", "10485760"))  # 10MB default
    ALLOWED_EXTENSIONS: set = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp"}
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    @classmethod
    def validate_config(cls):
        """Validate configuration"""
        if cls.OPENAI_API_KEY == "YOUR_OPENAI_API_KEY_HERE" or not cls.OPENAI_API_KEY:
            raise ValueError(
                "OPENAI_API_KEY environment variable is required. "
                "Please get your API key from https://platform.openai.com/api-keys"
            )

# Create global config instance
config = Config()