import json
import re
import logging
from typing import Dict, Any, Union
from datetime import datetime

from .simplified_client import ClankerClient
from .models import (
    ClankerResponse, ErrorResponse, MovieInfo, 
    DrinkRecommendation, DrinkType
)
from .config import config

logger = logging.getLogger(__name__)

class ClankerRecommender:
    """Clanker That Recommends Alcohol - Production-Ready Movie to Drink Recommender"""
    
    def __init__(self):
        """Initialize the recommender application"""
        logger.info("Initializing ClankerRecommender...")
        try:
            self.client = ClankerClient()
            logger.info("ClankerRecommender initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize ClankerRecommender: {str(e)}")
            raise
    
    def process_movie_data(self, movie_input: Union[str, Dict[str, Any]]) -> Union[ClankerResponse, ErrorResponse]:
        """
        Process movie data from frontend and return AI-generated drink recommendation
        
        Args:
            movie_input: JSON string or dictionary containing movie data from OMDB API
            
        Returns:
            ClankerResponse with structured drink recommendation or ErrorResponse on error
        """
        start_time = datetime.now()
        
        try:
            # Parse and validate the movie data
            movie_data = self._parse_and_validate_movie_data(movie_input)
            if isinstance(movie_data, ErrorResponse):
                return movie_data
            
            logger.info(f"Processing recommendation for: {movie_data['Title']} ({movie_data['Year']})")
            
            # Generate recommendation using the AI
            recommendation_text = self.client.generate_drink_recommendation(movie_data)
            
            # Parse the recommendation into structured data
            structured_recommendation = self._parse_recommendation(recommendation_text)
            
            # Create movie info object
            movie_info = MovieInfo(
                title=movie_data['Title'],
                year=movie_data['Year'],
                genre=movie_data['Genre'],
                runtime=movie_data.get('Runtime', 'N/A'),
                rating=movie_data.get('imdbRating', 'N/A'),
                director=movie_data['Director'],
                plot=movie_data.get('Plot', 'No plot available')
            )
            
            # Create formatted text for display
            formatted_text = self._create_formatted_text(movie_info, recommendation_text)
            
            # Calculate processing time
            processing_time = (datetime.now() - start_time).total_seconds()
            
            # Create the complete response
            response = ClankerResponse(
                success=True,
                movie=movie_info,
                recommendation=structured_recommendation,
                formatted_text=formatted_text,
                metadata={
                    "processing_time_seconds": processing_time,
                    "model_used": config.model_id,
                    "api_version": config.api_version,
                    "timestamp": datetime.now().isoformat()
                }
            )
            
            logger.info(f"Successfully processed recommendation in {processing_time:.2f}s")
            return response
            
        except Exception as e:
            logger.error(f"Error processing movie data: {str(e)}")
            return ErrorResponse(
                error=str(e),
                error_code="PROCESSING_ERROR",
                details={
                    "processing_time_seconds": (datetime.now() - start_time).total_seconds(),
                    "timestamp": datetime.now().isoformat()
                }
            )
    
    def _parse_and_validate_movie_data(self, movie_input: Union[str, Dict[str, Any]]) -> Union[Dict[str, Any], ErrorResponse]:
        """Parse and validate movie data input"""
        try:
            # Parse JSON string if needed
            if isinstance(movie_input, str):
                movie_data = json.loads(movie_input)
            else:
                movie_data = movie_input
            
            # Validate required fields
            required_fields = ['Title', 'Year', 'Genre', 'Director']
            missing_fields = [field for field in required_fields if not movie_data.get(field)]
            
            if missing_fields:
                return ErrorResponse(
                    error=f"Missing required movie data fields: {', '.join(missing_fields)}",
                    error_code="VALIDATION_ERROR",
                    details={"missing_fields": missing_fields}
                )
            
            return movie_data
            
        except json.JSONDecodeError as e:
            return ErrorResponse(
                error="Invalid JSON format for movie data",
                error_code="JSON_DECODE_ERROR",
                details={"json_error": str(e)}
            )
        except Exception as e:
            return ErrorResponse(
                error=f"Error validating movie data: {str(e)}",
                error_code="VALIDATION_ERROR"
            )
            
    def _parse_recommendation(self, text: str) -> DrinkRecommendation:
        """Parse the recommendation text into structured data with enhanced regex patterns"""
        
        logger.debug("Parsing recommendation text into structured data...")
        
        # Initialize with defaults
        result = {
            "name": "Unknown Drink",
            "type": DrinkType.COCKTAIL,
            "base": "Unknown base",
            "key_flavors": "Unknown flavors",
            "glass": "Standard glass",
            "garnish": None,
            "why_perfect": "Perfectly pairs with this movie",
            "experience": "Enhances the viewing experience",
            "recipe": "Recipe not available",
            "alcohol_content": None,
            "difficulty": None
        }
        
        # Enhanced regex patterns for more reliable parsing
        patterns = {
            "name": [
                r'Perfect Pairing:\s*(.+?)(?:\*\*|\n)',
                r'🍸\s*Perfect Pairing:\s*(.+?)(?:\*\*|\n)',
                r'Drink:\s*(.+?)(?:\*\*|\n)'
            ],
            "type": [
                r'Type:\s*(.+?)(?:\n|-)',
                r'Beverage Type:\s*(.+?)(?:\n|-)'
            ],
            "base": [
                r'Base:\s*(.+?)(?:\n|-)',
                r'Main ingredient[s]?:\s*(.+?)(?:\n|-)'
            ],
            "key_flavors": [
                r'Key flavors?:\s*(.+?)(?:\n|-)',
                r'Flavor profile:\s*(.+?)(?:\n|-)',
                r'Flavors?:\s*(.+?)(?:\n|-)'
            ],
            "glass": [
                r'Served in:\s*(.+?)(?:\n|-)',
                r'Glass:\s*(.+?)(?:\n|-)',
                r'Glassware:\s*(.+?)(?:\n|-)'
            ],
            "garnish": [
                r'Garnish/Accompaniment:\s*(.+?)(?:\n|\*\*)',
                r'Garnish:\s*(.+?)(?:\n|\*\*)',
                r'Accompaniment:\s*(.+?)(?:\n|\*\*)'
            ],
            "alcohol_content": [
                r'Alcohol Content:\s*(.+?)(?:\n|-)',
                r'ABV:\s*(.+?)(?:\n|-)',
                r'Strength:\s*(.+?)(?:\n|-)'
            ],
            "difficulty": [
                r'Difficulty:\s*(.+?)(?:\n|-)',
                r'Preparation:\s*(.+?)(?:\n|-)'
            ]
        }
        
        # Extract data using multiple pattern attempts
        for field, pattern_list in patterns.items():
            for pattern in pattern_list:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    value = match.group(1).strip()
                    if value and value.lower() not in ['none', 'n/a', 'unknown']:
                        result[field] = value
                    break
        
        # Extract why perfect and experience with multi-line support
        why_match = re.search(r'\*\*Why it\'s perfect:\*\*(.*?)(?:\*\*|$)', text, re.DOTALL | re.IGNORECASE)
        if why_match:
            result["why_perfect"] = why_match.group(1).strip()
        
        exp_match = re.search(r'\*\*The experience:\*\*(.*?)(?:\*\*|$)', text, re.DOTALL | re.IGNORECASE)
        if exp_match:
            result["experience"] = exp_match.group(1).strip()
        
        # Extract recipe with multiple possible headers
        recipe_patterns = [
            r'\*\*Quick Recipe[/:]?\*\*(.*?)(?:$|\n\n)',
            r'\*\*Recipe[/:]?\*\*(.*?)(?:$|\n\n)',
            r'\*\*Recommendation[/:]?\*\*(.*?)(?:$|\n\n)',
            r'\*\*How to make[/:]?\*\*(.*?)(?:$|\n\n)'
        ]
        
        for pattern in recipe_patterns:
            recipe_match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
            if recipe_match:
                result["recipe"] = recipe_match.group(1).strip()
                break
        
        # Normalize drink type
        if result["type"]:
            type_lower = result["type"].lower()
            if any(word in type_lower for word in ["cocktail", "mixed", "drink"]):
                result["type"] = DrinkType.COCKTAIL
            elif any(word in type_lower for word in ["wine", "vino", "vintage"]):
                result["type"] = DrinkType.WINE
            elif any(word in type_lower for word in ["beer", "ale", "lager", "stout", "ipa"]):
                result["type"] = DrinkType.BEER
            elif any(word in type_lower for word in ["spirit", "whiskey", "vodka", "gin", "rum", "tequila", "bourbon"]):
                result["type"] = DrinkType.SPIRIT
        
        logger.debug(f"Parsed recommendation: {result['name']} ({result['type']})")
        
        return DrinkRecommendation(**result)
    
    def _create_formatted_text(self, movie_info: MovieInfo, recommendation_text: str) -> str:
        """Create formatted markdown text for display"""
        
        return f"""## 🎬 {movie_info.title} ({movie_info.year})
**{movie_info.genre} • {movie_info.runtime} • ⭐ {movie_info.rating}/10**
*Directed by {movie_info.director}*

{recommendation_text}

---
*Recommendation generated by Clanker That Recommends Alcohol v{config.api_version}*"""
