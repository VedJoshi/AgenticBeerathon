#!/usr/bin/env python3
"""
Production startup script for Clanker That Recommends Alcohol API
"""

import os
import sys
import logging

# Set production environment
os.environ.setdefault("CLANKER_ENVIRONMENT", "production")
os.environ.setdefault("CLANKER_HOST", "0.0.0.0")
os.environ.setdefault("CLANKER_PORT", "8000")

def main():
    """Main entry point for production deployment"""
    try:
        # Add src to Python path
        src_path = os.path.join(os.path.dirname(__file__), 'src')
        if src_path not in sys.path:
            sys.path.insert(0, src_path)
        
        # Import the API module
        from beer_clanker_bot.api import app
        import uvicorn
        
        # Get configuration
        host = os.getenv("CLANKER_HOST", "0.0.0.0")
        port = int(os.getenv("CLANKER_PORT", os.getenv("PORT", "8000")))
        
        print(f"🍸 Starting Clanker API on {host}:{port}")
        
        # Run the server
        uvicorn.run(
            app,
            host=host,
            port=port,
            reload=False,
            access_log=True,
            log_level="info"
        )
        
    except Exception as e:
        print(f"❌ Failed to start server: {e}")
        logging.exception("Startup failed")
        sys.exit(1)

if __name__ == "__main__":
    main()
