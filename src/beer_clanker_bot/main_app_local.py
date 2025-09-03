from .omdb_client import OMDBClient
from .bedrock_client import BedrockClient
import pandas as pd
import os
from typing import List, Dict, Optional

class LocalCocktailClient:
    def __init__(self, csv_path: str):
        self.csv_path = csv_path
        self.cocktails_df = None
        self.load_cocktails()
    
    def load_cocktails(self):
        """Load cocktails from local CSV"""
        try:
            self.cocktails_df = pd.read_csv(self.csv_path)
            print(f"✅ Loaded {len(self.cocktails_df)} cocktails from local file")
        except Exception as e:
            print(f"❌ Error loading cocktails from {self.csv_path}: {e}")
            self.cocktails_df = pd.DataFrame()
    
    def search_cocktail(self, name: str) -> Optional[Dict]:
        """Search for cocktail by name"""
        if self.cocktails_df.empty:
            return None
            
        # Case-insensitive search
        matches = self.cocktails_df[
            self.cocktails_df['name'].str.contains(name, case=False, na=False)
        ]
        
        if not matches.empty:
            cocktail = matches.iloc[0]
            return {
                'name': cocktail.get('name', ''),
                'description': cocktail.get('description', ''),
                'ingredients': cocktail.get('ingredients', ''),
                'flavor_profile': cocktail.get('flavor_profile', ''),
                'tags': cocktail.get('tags', ''),
                'glass': cocktail.get('glass', ''),
                'method': cocktail.get('method', ''),
                'instructions': cocktail.get('instructions', '')
            }
        return None
    
    def get_cocktail_context(self, limit: int = 10) -> str:
        """Get sample cocktails for AI context"""
        if self.cocktails_df.empty:
            return "No cocktails available."
            
        sample = self.cocktails_df.head(limit) if len(self.cocktails_df) >= limit else self.cocktails_df
        
        context = "Available Cocktails:\n"
        for _, cocktail in sample.iterrows():
            context += f"- {cocktail.get('name', 'Unknown')}: {cocktail.get('description', 'No description')}\n"
            context += f"  Ingredients: {cocktail.get('ingredients', 'N/A')}\n"
            context += f"  Flavor: {cocktail.get('flavor_profile', 'N/A')}\n"
            context += f"  Glass: {cocktail.get('glass', 'N/A')}\n\n"
        
        return context
    
    def get_all_cocktail_names(self) -> List[str]:
        """Get list of all cocktail names for suggestions"""
        if self.cocktails_df.empty:
            return []
        return self.cocktails_df['name'].tolist()

class VinoFlixLocal:
    def __init__(self, csv_path: str = "sample_cocktails.csv"):
        omdb_key = os.getenv('OMDB_API_KEY')
        if not omdb_key:
            raise ValueError("OMDB_API_KEY environment variable is required")
        
        self.omdb = OMDBClient(omdb_key)
        self.bedrock = BedrockClient()
        # Keep cocktail_client for reverse lookup (cocktail to movie), but not for cocktail generation
        self.cocktail_client = LocalCocktailClient(csv_path)
    
    def get_recommendation(self, user_input: str) -> str:
        """Main recommendation logic"""
        
        # First check if it's a cocktail in local data
        cocktail = self.cocktail_client.search_cocktail(user_input)
        
        if cocktail:
            # It's a known cocktail → recommend movie
            return self.cocktail_to_movie(cocktail)
        else:
            # Check if it might be a cocktail name (contains common cocktail words)
            cocktail_indicators = ['martini', 'mojito', 'margarita', 'cocktail', 'punch', 'fizz', 'sour', 'old fashioned', 'manhattan', 'negroni', 'daiquiri', 'cosmopolitan', 'gimlet', 'tom collins', 'whiskey', 'gin', 'vodka', 'rum', 'tequila']
            user_input_lower = user_input.lower()
            
            # If input seems like a cocktail name, treat it as cocktail → movie
            if any(indicator in user_input_lower for indicator in cocktail_indicators) or len(user_input.split()) <= 3:
                return self.unknown_cocktail_to_movie(user_input)
            else:
                # Assume it's a movie → recommend cocktail
                return self.movie_to_cocktail(user_input)
    
    def movie_to_cocktail(self, movie_title: str) -> str:
        """Movie → AI-generated Cocktail recommendation"""
        
        # Get movie from OMDB
        movie = self.omdb.get_movie(movie_title)
        if not movie:
            return f"❌ Sorry, couldn't find the movie '{movie_title}'. Please try a different title."
        
        # Let AI create a cocktail recommendation without CSV constraints
        try:
            recommendation = self.bedrock.recommend_cocktail_for_movie(movie)
            
            return f"""
## 🎬 {movie['title']} ({movie['year']})
**{movie['genre']} • {movie['runtime']} • ⭐ {movie['imdb_rating']}/10**
*Directed by {movie['director']}*

{recommendation}

---
*Custom cocktail recommendation by AI*
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
    
    def unknown_cocktail_to_movie(self, cocktail_name: str) -> str:
        """Handle cocktail names not in our database → Movie recommendation"""
        
        try:
            recommendation = self.bedrock.recommend_movie_for_cocktail_name(cocktail_name)
            
            return f"""
## 🍸 {cocktail_name}

{recommendation}

---
*AI-powered pairing based on cocktail knowledge*
            """
            
        except Exception as e:
            return f"❌ Error getting recommendation: {str(e)}"
    
    def get_cocktail_suggestions(self) -> List[str]:
        """Get list of available cocktails for UI (now includes common cocktails beyond CSV)"""
        csv_cocktails = self.cocktail_client.get_all_cocktail_names()
        
        # Add common cocktails that AI can handle even if not in CSV
        common_cocktails = [
            "Martini", "Old Fashioned", "Manhattan", "Negroni", "Mojito", 
            "Margarita", "Cosmopolitan", "Daiquiri", "Whiskey Sour", "Tom Collins",
            "Gimlet", "Bloody Mary", "Piña Colada", "Moscow Mule", "Sazerac",
            "Vesper Martini", "White Russian", "French 75", "Aviation", "Last Word"
        ]
        
        # Combine and remove duplicates while preserving order
        all_cocktails = csv_cocktails + [c for c in common_cocktails if c not in csv_cocktails]
        return all_cocktails
