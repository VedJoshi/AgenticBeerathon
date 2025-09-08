import boto3
import json
import os
import logging
from typing import Dict, Any
from .config import config
from .models import DrinkType

logger = logging.getLogger(__name__)

class ClankerClient:
    """Enhanced AI client for Clanker That Recommends Alcohol"""
    
    def __init__(self):
        """Initialize the Bedrock client with configuration"""
        try:
            self.bedrock = boto3.client(
                'bedrock-runtime',
                region_name=config.aws_region,
                aws_access_key_id=config.aws_access_key_id,
                aws_secret_access_key=config.aws_secret_access_key
            )
            self.model_id = config.model_id
            logger.info(f"Initialized ClankerClient with model {self.model_id}")
        except Exception as e:
            logger.error(f"Failed to initialize Bedrock client: {str(e)}")
            raise
    
    def generate_drink_recommendation(self, movie_data: Dict[str, Any]) -> str:
        """Generate drink recommendation based on movie data from frontend"""
        
        logger.info(f"Generating recommendation for movie: {movie_data.get('Title', 'Unknown')}")
        
        # Extract relevant fields from the movie data
        title = movie_data.get('Title', 'Unknown')
        year = movie_data.get('Year', 'Unknown')
        genre = movie_data.get('Genre', 'Unknown')
        plot = movie_data.get('Plot', 'No plot available')
        director = movie_data.get('Director', 'Unknown')
        runtime = movie_data.get('Runtime', 'Unknown')
        rating = movie_data.get('imdbRating', 'N/A')
        
        # Construct the enhanced prompt for consistent structured output
        prompt = f"""You are "Clanker That Recommends Alcohol", an expert sommelier and mixologist AI. 
        
Analyze this movie and recommend the PERFECT alcoholic beverage pairing:

🎬 MOVIE DETAILS:
- Title: {title} ({year})
- Genre: {genre}
- Director: {director}
- Runtime: {runtime}
- IMDb Rating: {rating}
- Plot: {plot}

🍸 YOUR MISSION:
Recommend the ideal alcoholic beverage that captures this movie's essence. Consider:
- Movie's mood, themes, and atmosphere
- Historical period and setting
- Character personalities and sophistication level
- Color palette and aesthetic
- Emotional tone and viewing experience

DRINK OPTIONS: Consider ALL types:
- Cocktails (classic or creative)
- Wine (red, white, sparkling, dessert)
- Beer (craft, imported, specialty styles)  
- Spirits (neat, on rocks, simple mixers)

FORMAT YOUR RESPONSE EXACTLY AS FOLLOWS:

**🍸 Perfect Pairing: [EXACT DRINK NAME]**

**The Beverage:**
- Type: [Cocktail/Wine/Beer/Spirit]
- Base: [main alcohol/grape variety/beer style]
- Key flavors: [specific flavor notes]
- Served in: [specific glassware]
- Garnish/Accompaniment: [garnish or food pairing]
- Alcohol Content: [approximate ABV or strength]
- Difficulty: [Easy/Medium/Hard to make/find]

**Why it's perfect:**
[Write 2-3 compelling sentences explaining the connection between this drink and the movie's themes, mood, characters, or setting]

**The experience:**
[Describe how this drink enhances the movie-watching experience - sensory details, atmosphere, emotional connection]

**Quick Recipe/Recommendation:**
[If cocktail: precise measurements and method. If wine/beer: specific brands, vintages, or styles to look for]

Remember: Match the drink's sophistication to the movie. Classic films deserve timeless drinks, modern movies might call for contemporary choices, and cult films might need something unique or playful."""
        
        try:
            # Call the AI with the enhanced prompt
            response = self._call_claude(prompt)
            logger.info(f"Successfully generated recommendation for {title}")
            return response
        except Exception as e:
            logger.error(f"Error generating recommendation for {title}: {str(e)}")
            raise
    
    def _call_claude(self, prompt: str) -> str:
        """Internal method to call Claude API with enhanced error handling"""
        
        try:
            logger.debug("Calling Claude API...")
            
            # Use Claude's preferred message format with enhanced parameters
            request_body = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": config.max_tokens,
                "temperature": config.temperature,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            }
            
            # Call the Bedrock API with timeout
            response = self.bedrock.invoke_model(
                modelId=self.model_id,
                body=json.dumps(request_body)
            )
            
            # Parse response with error handling
            response_body = json.loads(response['body'].read().decode('utf-8'))
            
            if 'content' not in response_body or not response_body['content']:
                raise ValueError("Empty response from Claude API")
                
            content = response_body['content'][0]['text']
            logger.debug(f"Claude API response length: {len(content)} characters")
            
            return content
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error from Claude API: {str(e)}")
            raise ValueError("Invalid response format from AI service")
        except Exception as e:
            logger.error(f"Error calling Claude API: {str(e)}")
            if "throttling" in str(e).lower():
                raise ValueError("AI service is temporarily busy. Please try again in a moment.")
            elif "authentication" in str(e).lower():
                raise ValueError("AI service authentication failed. Please check configuration.")
            else:
                raise ValueError(f"AI service error: {str(e)}")
