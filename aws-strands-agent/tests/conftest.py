"""
Test configuration and utilities
"""
import pytest
import asyncio
from src.utils.config import Config


@pytest.fixture
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def mock_config():
    """Mock configuration for testing"""
    return {
        "AWS_REGION": "us-east-1",
        "BEDROCK_MODEL_ID": "anthropic.claude-3-sonnet-20240229-v1:0",
        "APP_NAME": "test-app",
        "LOG_LEVEL": "DEBUG"
    }
