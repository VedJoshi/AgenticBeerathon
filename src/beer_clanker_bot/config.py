"""
Configuration management for Clanker That Recommends Alcohol
"""
import os
from typing import Optional
import logging

class ClankerConfig:
    """Application configuration with environment variable support"""
    
    def __init__(self):
        # AWS Configuration
        self.aws_region = os.getenv("CLANKER_AWS_REGION", os.getenv("AWS_REGION", "us-east-1"))
        self.aws_access_key_id = os.getenv("CLANKER_AWS_ACCESS_KEY_ID", os.getenv("AWS_ACCESS_KEY_ID"))
        self.aws_secret_access_key = os.getenv("CLANKER_AWS_SECRET_ACCESS_KEY", os.getenv("AWS_SECRET_ACCESS_KEY"))
        
        # AI Model Configuration
        self.model_id = os.getenv("CLANKER_MODEL_ID", "anthropic.claude-3-sonnet-20240229-v1:0")
        self.max_tokens = int(os.getenv("CLANKER_MAX_TOKENS", "1500"))
        self.temperature = float(os.getenv("CLANKER_TEMPERATURE", "0.7"))
        
        # API Configuration
        self.api_title = os.getenv("CLANKER_API_TITLE", "Clanker That Recommends Alcohol API")
        self.api_description = os.getenv("CLANKER_API_DESCRIPTION", "Production-ready API for generating personalized beverage recommendations based on movie data")
        self.api_version = os.getenv("CLANKER_API_VERSION", "2.0.0")
        self.port = int(os.getenv("CLANKER_PORT", os.getenv("PORT", "8000")))
        self.host = os.getenv("CLANKER_HOST", "0.0.0.0")
        
        # Logging Configuration
        self.log_level = os.getenv("CLANKER_LOG_LEVEL", "INFO")
        self.log_format = os.getenv("CLANKER_LOG_FORMAT", "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        
        # Rate Limiting
        self.rate_limit_per_minute = int(os.getenv("CLANKER_RATE_LIMIT_PER_MINUTE", "60"))
        self.rate_limit_burst = int(os.getenv("CLANKER_RATE_LIMIT_BURST", "10"))
        
        # Request Timeout
        self.request_timeout = int(os.getenv("CLANKER_REQUEST_TIMEOUT", "30"))
        
        # Environment
        self.environment = os.getenv("CLANKER_ENVIRONMENT", os.getenv("ENVIRONMENT", "development"))
        self.debug = os.getenv("CLANKER_DEBUG", os.getenv("DEBUG", "false")).lower() in ("true", "1", "yes")

# Global configuration instance
config = ClankerConfig()

def setup_logging():
    """Configure application logging"""
    logging.basicConfig(
        level=getattr(logging, config.log_level.upper()),
        format=config.log_format
    )
    
    # Suppress noisy third-party loggers in production
    if config.environment == "production":
        logging.getLogger("boto3").setLevel(logging.WARNING)
        logging.getLogger("botocore").setLevel(logging.WARNING)
        logging.getLogger("urllib3").setLevel(logging.WARNING)

def is_production() -> bool:
    """Check if running in production environment"""
    return config.environment.lower() == "production"

def is_development() -> bool:
    """Check if running in development environment"""
    return config.environment.lower() in ["development", "dev"]
