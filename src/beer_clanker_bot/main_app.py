from .omdb_client import OMDBClient
from .bedrock_client import BedrockClient
from .s3_client import S3CocktailClient
import os
from typing import List

class VinoFlix:
    def __init__(self, s3_bucket: str, s3_csv_key: str):
        omdb_key = os.getenv('OMDB_API_KEY')
        if not omdb_key:
            raise ValueError("OMDB_API_KEY environment variable is required")
        
        self.omdb = OMDBClient(omdb_key)
        self.bedrock = BedrockClient()
        self.cocktail_client = S3CocktailClient(s3_bucket, s3_csv_key)
    
    def get_recommendation(self, user_input: str) -> str:
        """Main recommendation logic"""
        
        # First check if it's a cocktail in S3 data
        cocktail = self.cocktail_client.search_cocktail(user_input)
        
        if cocktail:
            # It's a cocktail → recommend movie
            return self.cocktail_to_movie(cocktail)
        else:
            # Assume it's a movie → recommend cocktail
            return self.movie_to_cocktail(user_input)
    
    def movie_to_cocktail(self, movie_title: str) -> str:
        """Movie → Cocktail recommendation using S3 data"""
        
        # Get movie from OMDB
        movie = self.omdb.get_movie(movie_title)
        if not movie:
            return f"❌ Sorry, couldn't find the movie '{movie_title}'. Please try a different title."
        
        # Get cocktail context from S3
        cocktail_context = self.cocktail_client.get_cocktail_context(15)  # Use more cocktails for context
        
        # Get AI recommendation
        try:
            recommendation = self.bedrock.recommend_cocktail_for_movie(movie, cocktail_context)
            
            return f"""
## 🎬 {movie['title']} ({movie['year']})
**{movie['genre']} • {movie['runtime']} • ⭐ {movie['imdb_rating']}/10**
*Directed by {movie['director']}*

{recommendation}

---
*Recommendation based on your cocktail collection*
            """
            
        except Exception as e:
            return f"❌ Error getting recommendation: {str(e)}"
    
    def cocktail_to_movie(self, cocktail_data: dict) -> str:
        """Cocktail → Movie recommendation"""
        
        try:
            recommendation = self.bedrock.recommend_movie_for_cocktail(cocktail_data)
            
            return f"""
## 🍸 {cocktail_data['name']}
*{cocktail_data['description']}*
**Served in:** {cocktail_data['glass']} • **Method:** {cocktail_data['method']}

{recommendation}

---
*Based on this cocktail's character and flavor profile*
            """
            
        except Exception as e:
            return f"❌ Error getting recommendation: {str(e)}"
    
    def get_cocktail_suggestions(self) -> List[str]:
        """Get list of available cocktails for UI"""
        return self.cocktail_client.get_all_cocktail_names()[:20]  # First 20 for suggestions
