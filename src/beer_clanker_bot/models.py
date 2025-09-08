"""
Data models for Clanker That Recommends Alcohol API
"""
from pydantic import BaseModel, Field, validator
from typing import Dict, Any, Optional, List
from enum import Enum

class DrinkType(str, Enum):
    """Enumeration of drink types"""
    COCKTAIL = "cocktail"
    WINE = "wine"
    BEER = "beer"
    SPIRIT = "spirit"

class MovieData(BaseModel):
    """Input schema for movie data from OMDB API"""
    movie_data: Dict[str, Any] = Field(
        ..., 
        description="Movie data object from OMDB API",
        example={
            "Title": "Casablanca",
            "Year": "1942",
            "Genre": "Drama, Romance, War",
            "Director": "Michael Curtiz",
            "Plot": "A cynical expatriate American cafe owner...",
            "Runtime": "102 min",
            "imdbRating": "8.5"
        }
    )
    
    @validator('movie_data')
    def validate_required_fields(cls, v):
        """Validate that required movie fields are present"""
        required_fields = ['Title', 'Year', 'Genre', 'Director']
        missing_fields = [field for field in required_fields if field not in v]
        if missing_fields:
            raise ValueError(f"Missing required fields: {', '.join(missing_fields)}")
        return v

class MovieInfo(BaseModel):
    """Movie information structure"""
    title: str = Field(..., description="Movie title")
    year: str = Field(..., description="Release year")
    genre: str = Field(..., description="Movie genres")
    runtime: Optional[str] = Field(None, description="Runtime duration")
    rating: Optional[str] = Field(None, description="IMDb rating")
    director: str = Field(..., description="Movie director(s)")
    plot: Optional[str] = Field(None, description="Movie plot summary")

class DrinkRecommendation(BaseModel):
    """Structured drink recommendation"""
    name: str = Field(..., description="Name of the recommended drink")
    type: DrinkType = Field(..., description="Type of alcoholic beverage")
    base: str = Field(..., description="Main ingredients or base spirits")
    key_flavors: str = Field(..., description="Primary flavor profile")
    glass: str = Field(..., description="Recommended glassware")
    garnish: Optional[str] = Field(None, description="Garnish or accompaniment")
    why_perfect: str = Field(..., description="Explanation of why this drink pairs with the movie")
    experience: str = Field(..., description="Description of the drinking experience with the movie")
    recipe: str = Field(..., description="Recipe instructions or brand recommendations")
    alcohol_content: Optional[str] = Field(None, description="Estimated alcohol content")
    difficulty: Optional[str] = Field(None, description="Preparation difficulty (Easy/Medium/Hard)")

class ClankerResponse(BaseModel):
    """Complete API response structure"""
    success: bool = Field(True, description="Whether the request was successful")
    movie: MovieInfo = Field(..., description="Movie information")
    recommendation: DrinkRecommendation = Field(..., description="Drink recommendation details")
    formatted_text: Optional[str] = Field(None, description="Formatted markdown text for display")
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata about the recommendation"
    )

class ErrorResponse(BaseModel):
    """Error response structure"""
    success: bool = Field(False, description="Always false for error responses")
    error: str = Field(..., description="Error message")
    error_code: str = Field(..., description="Error code for programmatic handling")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")

class HealthResponse(BaseModel):
    """Health check response"""
    status: str = Field(..., description="Service status")
    service: str = Field(..., description="Service name")
    version: str = Field(..., description="API version")
    timestamp: str = Field(..., description="Current timestamp")
