import os
from typing import Optional

class Config:
    """Application configuration"""
    
    # Google Cloud Vision
    GOOGLE_APPLICATION_CREDENTIALS: Optional[str] = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    
    # API Configuration
    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
    API_PORT: int = int(os.getenv("API_PORT", "8000"))
    
    # File Upload Limits
    MAX_FILE_SIZE: int = int(os.getenv("MAX_FILE_SIZE", "10485760"))  # 10MB default
    ALLOWED_EXTENSIONS: set = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp"}
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    @classmethod
    def validate_config(cls):
        """Validate required configuration"""
        if not cls.GOOGLE_APPLICATION_CREDENTIALS:
            raise ValueError(
                "GOOGLE_APPLICATION_CREDENTIALS environment variable is required. "
                "Please set it to the path of your Google Cloud service account key file."
            )

# Create global config instance
config = Config()