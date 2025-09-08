#!/usr/bin/env python3
"""
Simple deployment utility for Clanker That Recommends Alcohol
"""

import os
import sys

def check_dependencies():
    """Check if required dependencies are installed"""
    try:
        import boto3
        import fastapi
        import uvicorn
        import pydantic
        print("✅ All dependencies are installed")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Run 'pip install -r requirements.txt' to install dependencies")
        return False

def run_local():
    """Run the API server locally"""
    if not check_dependencies():
        return
    
    print("\n🚀 Starting API server locally...")
    print("Server will be available at http://localhost:8000")
    
    # Set environment for local development
    os.environ.setdefault("CLANKER_ENVIRONMENT", "development")
    os.environ.setdefault("CLANKER_DEBUG", "true")
    
    # Import and run the API
    try:
        from src.beer_clanker_bot.api import app
        import uvicorn
        uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
    except Exception as e:
        print(f"❌ Failed to start server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    print("🍸🎬 Clanker That Recommends Alcohol - Local Development")
    print("=" * 60)
    run_local()
