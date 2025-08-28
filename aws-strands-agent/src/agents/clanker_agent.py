"""
Clanker Basic Agent - MVP Version
Simple movie-to-cocktail recommendation engine
"""
import asyncio
import sys
import os

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.movie_tool import MovieTool
from tools.cocktail_tool import CocktailTool
from typing import Dict, Optional, List
import random

class ClankerAgent:
    """Basic agent for movie-to-cocktail recommendations"""
    
    def __init__(self):
        self.movie_tool = MovieTool()
        self.cocktail_tool = CocktailTool()
        
        # Simple genre-to-mood mapping for MVP
        self.genre_mappings = {
            'action': 'strong',
            'adventure': 'strong', 
            'thriller': 'strong',
            'comedy': 'refreshing',
            'romance': 'elegant',
            'drama': 'sophisticated',
            'horror': 'strong',
            'mystery': 'sophisticated',
            'sci-fi': 'modern',
            'fantasy': 'tropical',
            'musical': 'elegant',
            'western': 'strong',
            'war': 'strong',
            'crime': 'sophisticated',
            'family': 'refreshing',
            'animation': 'tropical'
        }
    
    async def recommend_cocktail_for_movie(self, movie_title: str) -> Dict:
        """
        Get cocktail recommendation for a movie
        
        Args:
            movie_title (str): Movie title
            
        Returns:
            Dict: Recommendation with movie data, cocktail, and explanation
        """
        try:
            # Get movie data
            movie = await self.movie_tool.search_movie(movie_title)
            if not movie:
                return {
                    'success': False,
                    'error': f"Movie '{movie_title}' not found",
                    'movie': None,
                    'cocktail': None,
                    'explanation': None
                }
            
            # Determine mood based on genre
            mood = self._get_mood_from_movie(movie)
            
            # Get cocktail recommendation
            cocktail = await self._get_cocktail_for_mood(mood, movie)
            
            if not cocktail:
                # Fallback to random cocktail
                cocktail = await self.cocktail_tool.get_random_cocktail()
                mood = 'surprise'
            
            # Generate explanation
            explanation = self._generate_explanation(movie, cocktail, mood)
            
            return {
                'success': True,
                'movie': {
                    'title': movie['title'],
                    'year': movie['year'],
                    'genre': movie['genre'],
                    'director': movie['director'],
                    'imdb_rating': movie['imdb_rating'],
                    'plot': movie['plot'][:200] + '...' if len(movie['plot']) > 200 else movie['plot']
                },
                'cocktail': {
                    'name': cocktail['name'],
                    'ingredients': cocktail['ingredients'][:5],  # Limit ingredients shown
                    'instructions': cocktail['instructions'][:300] + '...' if len(cocktail['instructions']) > 300 else cocktail['instructions'],
                    'glass': cocktail['glass'],
                    'tags': cocktail.get('tags', [])
                },
                'explanation': explanation,
                'mood': mood,
                'confidence': 'Medium'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f"Error generating recommendation: {str(e)}",
                'movie': None,
                'cocktail': None,
                'explanation': None
            }
    
    def _get_mood_from_movie(self, movie: Dict) -> str:
        """Determine mood from movie genres"""
        genres = movie.get('genre', '').lower()
        
        # Check each genre mapping
        for genre, mood in self.genre_mappings.items():
            if genre in genres:
                return mood
        
        # Default mood
        return 'classic'
    
    async def _get_cocktail_for_mood(self, mood: str, movie: Dict) -> Optional[Dict]:
        """Get cocktail that matches the mood"""
        try:
            # Get cocktails by mood
            mood_cocktails = self.cocktail_tool.get_cocktails_by_mood(mood)
            
            if mood_cocktails:
                return random.choice(mood_cocktails)
            
            # Fallback to classic cocktails
            classic_cocktails = self.cocktail_tool.get_cocktails_by_mood('classic')
            if classic_cocktails:
                return random.choice(classic_cocktails)
            
            # Final fallback
            return await self.cocktail_tool.get_random_cocktail()
            
        except Exception as e:
            print(f"Error getting cocktail for mood '{mood}': {str(e)}")
            return await self.cocktail_tool.get_random_cocktail()
    
    def _generate_explanation(self, movie: Dict, cocktail: Dict, mood: str) -> str:
        """Generate explanation for the pairing"""
        movie_title = movie.get('title', '')
        cocktail_name = cocktail.get('name', '')
        genre = movie.get('genre', '')
        
        # Template explanations based on mood
        explanations = {
            'strong': f"The bold, intense flavors of a {cocktail_name} perfectly complement the action-packed energy of {movie_title}. Both pack a punch and leave a lasting impression.",
            
            'elegant': f"The sophisticated {cocktail_name} mirrors the refined storytelling of {movie_title}. Like the film's elegant cinematography, this cocktail is a work of art in a glass.",
            
            'refreshing': f"The light, refreshing {cocktail_name} captures the uplifting spirit of {movie_title}. Both offer a delightful escape from the everyday.",
            
            'sophisticated': f"The complex layers of a {cocktail_name} echo the nuanced storytelling in {movie_title}. Both reward careful attention and reveal new depths with each experience.",
            
            'tropical': f"The exotic flavors of a {cocktail_name} transport you to the imaginative world of {movie_title}. Both offer an escape to somewhere magical.",
            
            'modern': f"The innovative {cocktail_name} matches the cutting-edge style of {movie_title}. Both represent the perfect fusion of tradition and innovation.",
            
            'classic': f"The timeless {cocktail_name} pairs beautifully with the enduring appeal of {movie_title}. Some combinations are simply meant to be.",
            
            'surprise': f"Sometimes the best pairings are unexpected! The unique {cocktail_name} offers an intriguing counterpoint to {movie_title}, creating a memorable experience."
        }
        
        base_explanation = explanations.get(mood, explanations['classic'])
        
        # Add specific details if available
        details = []
        if movie.get('imdb_rating') and float(movie['imdb_rating']) > 8.0:
            details.append("This acclaimed film deserves an equally exceptional drink.")
        
        if 'vintage' in cocktail_name.lower() or any(tag.lower() in ['classic', 'traditional'] for tag in cocktail.get('tags', [])):
            details.append("This classic cocktail brings timeless elegance to your viewing experience.")
        
        if details:
            return base_explanation + " " + " ".join(details)
        
        return base_explanation
    
    def sync_recommend(self, movie_title: str) -> Dict:
        """Synchronous version for easy testing"""
        try:
            # Get movie data synchronously
            movie = self.movie_tool.sync_search_movie(movie_title)
            if not movie:
                return {
                    'success': False,
                    'error': f"Movie '{movie_title}' not found",
                    'movie': None,
                    'cocktail': None,
                    'explanation': None
                }
            
            # Determine mood based on genre
            mood = self._get_mood_from_movie(movie)
            
            # Get cocktail recommendation synchronously
            cocktail = self._sync_get_cocktail_for_mood(mood, movie)
            
            if not cocktail:
                # Fallback to random cocktail
                cocktail = self.cocktail_tool.sync_get_random_cocktail()
                mood = 'surprise'
            
            # Generate explanation
            explanation = self._generate_explanation(movie, cocktail, mood)
            
            return {
                'success': True,
                'movie': {
                    'title': movie['title'],
                    'year': movie['year'],
                    'genre': movie['genre'],
                    'director': movie['director'],
                    'imdb_rating': movie['imdb_rating'],
                    'plot': movie['plot'][:200] + '...' if len(movie['plot']) > 200 else movie['plot']
                },
                'cocktail': {
                    'name': cocktail['name'],
                    'ingredients': cocktail['ingredients'][:5],  # Limit ingredients shown
                    'instructions': cocktail['instructions'][:300] + '...' if len(cocktail['instructions']) > 300 else cocktail['instructions'],
                    'glass': cocktail['glass'],
                    'tags': cocktail.get('tags', [])
                },
                'explanation': explanation,
                'mood': mood,
                'confidence': 'Medium'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f"Error generating recommendation: {str(e)}",
                'movie': None,
                'cocktail': None,
                'explanation': None
            }
    
    def _sync_get_cocktail_for_mood(self, mood: str, movie: Dict) -> Optional[Dict]:
        """Get cocktail that matches the mood - synchronous version"""
        try:
            # Get cocktails by mood
            mood_cocktails = self.cocktail_tool.get_cocktails_by_mood(mood)
            
            if mood_cocktails:
                return random.choice(mood_cocktails)
            
            # Fallback to classic cocktails
            classic_cocktails = self.cocktail_tool.get_cocktails_by_mood('classic')
            if classic_cocktails:
                return random.choice(classic_cocktails)
            
            # Final fallback
            return self.cocktail_tool.sync_get_random_cocktail()
            
        except Exception as e:
            print(f"Error getting cocktail for mood '{mood}': {str(e)}")
            return self.cocktail_tool.sync_get_random_cocktail()

# Convenience function for quick testing
def quick_recommendation(movie_title: str) -> Dict:
    """Quick movie recommendation"""
    agent = ClankerAgent()
    return agent.sync_recommend(movie_title)

# Test the agent if run directly
if __name__ == "__main__":
    print("🎬🍸 Clanker MVP Agent - Testing...")
    
    agent = ClankerAgent()
    
    # Test cases
    test_movies = [
        "The Grand Budapest Hotel",
        "Blade Runner 2049", 
        "Mad Max: Fury Road"
    ]
    
    for movie in test_movies:
        print(f"\n{'='*50}")
        print(f"🎬 Testing: {movie}")
        print('='*50)
        
        result = agent.sync_recommend(movie)
        
        if result['success']:
            print(f"🎬 Movie: {result['movie']['title']} ({result['movie']['year']})")
            print(f"🎭 Genre: {result['movie']['genre']}")
            print(f"⭐ Rating: {result['movie']['imdb_rating']}")
            print(f"\n🍸 Recommended: {result['cocktail']['name']}")
            print(f"🥃 Glass: {result['cocktail']['glass']}")
            print(f"🧪 Ingredients: {', '.join(result['cocktail']['ingredients'][:3])}...")
            print(f"\n💭 Why this pairing:")
            print(f"   {result['explanation']}")
            print(f"\n🎯 Mood: {result['mood']} | Confidence: {result['confidence']}")
        else:
            print(f"❌ Error: {result['error']}")
    
    print(f"\n{'='*50}")
    print("🎉 MVP Testing Complete!")
    print("Ready for interactive use! 🚀")
