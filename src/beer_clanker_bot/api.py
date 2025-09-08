"""
Production-ready FastAPI application for Clanker That Recommends Alcohol
"""
from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import logging
import time
from datetime import datetime
from typing import Dict, Any
import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from beer_clanker_bot.simplified_app import ClankerRecommender
from beer_clanker_bot.models import (
    MovieData, ClankerResponse, ErrorResponse, HealthResponse
)
from beer_clanker_bot.config import config, setup_logging

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

# Initialize FastAPI app with enhanced configuration
app = FastAPI(
    title=config.api_title,
    description=config.api_description,
    version=config.api_version,
    docs_url="/docs" if config.debug else None,
    redoc_url="/redoc" if config.debug else None,
    openapi_url="/openapi.json" if config.debug else None,
)

# Add security middleware for production
if not config.debug:
    app.add_middleware(
        TrustedHostMiddleware, 
        allowed_hosts=["*"]  # Configure with actual allowed hosts in production
    )

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://beerathon.streamlit.app",
        "http://localhost:8501",  # For local testing
        "http://localhost:3000",  # For local frontend dev
        "*" if config.debug else "https://beerathon.streamlit.app"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler for unhandled errors"""
    logger.error(f"Unhandled exception on {request.url}: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            error="Internal server error",
            error_code="INTERNAL_ERROR",
            details={"timestamp": datetime.now().isoformat()}
        ).dict()
    )

# Request timing middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """Add processing time to response headers"""
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    logger.info(f"{request.method} {request.url} - {response.status_code} - {process_time:.3f}s")
    return response

# Initialize recommender (singleton pattern)
_recommender = None

def get_recommender() -> ClankerRecommender:
    """Dependency to get the recommender instance"""
    global _recommender
    if _recommender is None:
        try:
            logger.info("Initializing ClankerRecommender...")
            _recommender = ClankerRecommender()
            logger.info("ClankerRecommender initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize ClankerRecommender: {str(e)}")
            raise HTTPException(
                status_code=503,
                detail=ErrorResponse(
                    error="Service initialization failed",
                    error_code="INIT_ERROR",
                    details={"message": "Unable to initialize AI recommendation service"}
                ).dict()
            )
    return _recommender

@app.post("/recommend-drink/", response_model=ClankerResponse)
async def recommend_drink(
    data: MovieData, 
    recommender: ClankerRecommender = Depends(get_recommender)
) -> ClankerResponse:
    """
    🍸 Generate a personalized alcoholic beverage recommendation based on movie data
    
    This endpoint analyzes movie characteristics (genre, plot, mood, era) and returns
    the perfect drink pairing to enhance your movie-watching experience.
    
    **Supported drink types:**
    - Classic and creative cocktails
    - Fine wines (red, white, sparkling)
    - Craft beers and specialty brews
    - Premium spirits and liqueurs
    
    **Input Requirements:**
    - Movie data from OMDB API format
    - Required fields: Title, Year, Genre, Director
    - Optional: Plot, Runtime, imdbRating for better recommendations
    
    **Response includes:**
    - Complete structured drink details
    - Step-by-step recipe or purchase recommendations
    - Explanation of why this drink pairs perfectly
    - Formatted text for display purposes
    """
    try:
        logger.info(f"Processing recommendation request for: {data.movie_data.get('Title', 'Unknown')}")
        
        # Process the movie data
        result = recommender.process_movie_data(data.movie_data)
        
        # Handle error responses
        if isinstance(result, ErrorResponse):
            logger.warning(f"Request failed: {result.error}")
            raise HTTPException(
                status_code=400, 
                detail=result.dict()
            )
        
        logger.info(f"Successfully generated recommendation for: {data.movie_data.get('Title', 'Unknown')}")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error processing request: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=ErrorResponse(
                error="Failed to generate recommendation",
                error_code="PROCESSING_ERROR",
                details={"timestamp": datetime.now().isoformat()}
            ).dict()
        )

@app.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """
    🩺 Health check endpoint for monitoring service status
    
    Returns current service status, version, and operational metrics.
    Used by load balancers and monitoring systems.
    """
    try:
        # Basic health check without initializing AWS services
        return HealthResponse(
            status="healthy",
            service="Clanker That Recommends Alcohol",
            version=config.api_version,
            timestamp=datetime.now().isoformat()
        )
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(
            status_code=503,
            detail=HealthResponse(
                status="unhealthy",
                service="Clanker That Recommends Alcohol", 
                version=config.api_version,
                timestamp=datetime.now().isoformat()
            ).dict()
        )

@app.get("/health/aws")
async def aws_health_check():
    """
    🔧 AWS connectivity health check
    Tests if AWS services are accessible and properly configured
    """
    try:
        # Test AWS connection by initializing recommender
        get_recommender()
        return {
            "status": "healthy",
            "aws_connection": "active",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"AWS health check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "aws_connection": "failed",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@app.get("/")
async def root():
    """
    🏠 Root endpoint with API information
    """
    return {
        "service": "Clanker That Recommends Alcohol",
        "version": config.api_version,
        "description": "AI-powered beverage recommendations for movies",
        "endpoints": {
            "recommend": "/recommend-drink/",
            "health": "/health",
            "docs": "/docs" if config.debug else "Documentation disabled in production"
        },
        "status": "operational"
    }

if __name__ == "__main__":
    # Run the API server if this file is executed directly
    logger.info(f"Starting Clanker API server on {config.host}:{config.port}")
    logger.info(f"Environment: {config.environment}")
    logger.info(f"Debug mode: {config.debug}")
    
    uvicorn.run(
        app,
        host=config.host,
        port=config.port,
        reload=config.debug,
        access_log=config.debug,
        log_level=config.log_level.lower()
    )
