#!/usr/bin/env python3
"""
🎬🍸 Movie & Cocktail AI Demo
Complete working demo of your AI-powered recommendation system
"""

import asyncio
import os
import sys
import json
from typing import Dict, Optional
import boto3
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add src to path so we can import our modules
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

class MovieCocktailAgent:
    """AI agent that recommends cocktails for movies"""
    
    def __init__(self):
        self.setup_aws()
        self.load_cocktail_data()
        self.load_movie_data()
        
    def setup_aws(self):
        """Initialize AWS Bedrock client"""
        try:
            self.bedrock_client = boto3.client(
                'bedrock-runtime',
                region_name=os.getenv('AWS_REGION', 'us-east-1')
            )
            self.model_id = os.getenv('BEDROCK_MODEL_ID', 'anthropic.claude-3-sonnet-20240229-v1:0')
            print("✅ AWS Bedrock initialized successfully!")
        except Exception as e:
            print(f"⚠️ AWS Bedrock initialization failed: {e}")
            self.bedrock_client = None
            
    def load_cocktail_data(self):
        """Load cocktail database"""
        try:
            # Try to load from your data directory
            cocktail_files = [
                'data/cocktails/data/cocktails',
                'src/data/cocktails', 
                'cocktail_data.json'
            ]
            
            self.cocktails = {}
            
            # For demo purposes, let's add some sample cocktails
            self.cocktails = {
                'martini': {
                    'name': 'Martini',
                    'ingredients': ['gin', 'dry vermouth', 'olive'],
                    'glass': 'martini glass',
                    'category': 'classic',
                    'tags': ['elegant', 'strong', 'sophisticated']
                },
                'old_fashioned': {
                    'name': 'Old Fashioned',
                    'ingredients': ['whiskey', 'sugar', 'bitters', 'orange'],
                    'glass': 'rocks glass',
                    'category': 'classic',
                    'tags': ['traditional', 'strong', 'bitter']
                },
                'margarita': {
                    'name': 'Margarita',
                    'ingredients': ['tequila', 'lime juice', 'triple sec'],
                    'glass': 'margarita glass',
                    'category': 'tropical',
                    'tags': ['citrus', 'refreshing', 'party']
                },
                'negroni': {
                    'name': 'Negroni',
                    'ingredients': ['gin', 'campari', 'sweet vermouth'],
                    'glass': 'rocks glass',
                    'category': 'bitter',
                    'tags': ['bitter', 'sophisticated', 'italian']
                },
                'manhattan': {
                    'name': 'Manhattan',
                    'ingredients': ['whiskey', 'sweet vermouth', 'bitters'],
                    'glass': 'coupe glass',
                    'category': 'classic',
                    'tags': ['sophisticated', 'strong', 'traditional']
                }
            }
            print(f"✅ Loaded {len(self.cocktails)} cocktails")
            
        except Exception as e:
            print(f"⚠️ Error loading cocktail data: {e}")
            self.cocktails = {}
            
    def load_movie_data(self):
        """Load movie database (using OMDB API or mock data)"""
        self.omdb_api_key = os.getenv('OMDB_API_KEY')
        print(f"✅ Movie API {'configured' if self.omdb_api_key else 'using mock data'}")
        
    async def get_cocktail_for_movie(self, movie_title: str) -> Dict:
        """Get AI-powered cocktail recommendation for a movie"""
        try:
            # First get movie details
            movie_info = await self.get_movie_info(movie_title)
            
            # Then get AI recommendation
            ai_response = await self.get_ai_recommendation(movie_info)
            
            # Find the recommended cocktail in our database
            recommended_cocktail = self.find_cocktail(ai_response.get('cocktail_name', ''))
            
            return {
                'success': True,
                'movie': movie_info,
                'cocktail': recommended_cocktail,
                'explanation': ai_response.get('explanation', ''),
                'alternatives': ai_response.get('alternatives', []),
                'confidence': ai_response.get('confidence', 'Medium')
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'movie': None,
                'cocktail': None
            }
    
    async def get_movie_info(self, movie_title: str) -> Dict:
        """Get movie information"""
        # Mock movie data for demo - in real system would use OMDB API
        mock_movies = {
            'casablanca': {
                'title': 'Casablanca',
                'year': '1942',
                'genre': 'Drama, Romance, War',
                'director': 'Michael Curtiz',
                'plot': 'A cynical American expatriate struggles to decide whether to help his former lover and her fugitive husband escape French Morocco.',
                'imdb_rating': '8.5'
            },
            'blade runner 2049': {
                'title': 'Blade Runner 2049',
                'year': '2017',
                'genre': 'Action, Drama, Mystery',
                'director': 'Denis Villeneuve',
                'plot': 'A young blade runner discovers a secret that could end replicant slavery.',
                'imdb_rating': '8.0'
            },
            'her': {
                'title': 'Her',
                'year': '2013',
                'genre': 'Drama, Romance, Sci-Fi',
                'director': 'Spike Jonze',
                'plot': 'A sensitive writer develops a relationship with an AI operating system.',
                'imdb_rating': '8.0'
            }
        }
        
        movie_key = movie_title.lower()
        if movie_key in mock_movies:
            return mock_movies[movie_key]
        else:
            # Default movie info
            return {
                'title': movie_title,
                'year': 'Unknown',
                'genre': 'Unknown',
                'director': 'Unknown',
                'plot': f'Movie: {movie_title}',
                'imdb_rating': 'N/A'
            }
    
    async def get_ai_recommendation(self, movie_info: Dict) -> Dict:
        """Get AI-powered cocktail recommendation"""
        
        if not self.bedrock_client:
            return self.get_fallback_recommendation(movie_info)
        
        try:
            # Create AI prompt
            prompt = f"""You are an expert sommelier and film critic who specializes in pairing cocktails with movies.

MOVIE TO ANALYZE:
Title: {movie_info['title']}
Year: {movie_info['year']}
Genre: {movie_info['genre']}
Director: {movie_info['director']}
Plot: {movie_info['plot']}
IMDB Rating: {movie_info['imdb_rating']}

AVAILABLE COCKTAILS: {', '.join(self.cocktails.keys())}

TASK: Recommend the perfect cocktail for watching this movie.

Consider:
1. Movie's mood, atmosphere, and tone
2. Historical period and setting
3. Character sophistication level
4. Viewing experience (tension, romance, action)
5. Time of day best for watching

Respond with a JSON object:
{{
    "cocktail_name": "exact_cocktail_name",
    "explanation": "2-3 sentence explanation of why this pairing works",
    "confidence": "High/Medium/Low",
    "alternatives": ["alternative1", "alternative2"],
    "reasoning": "step-by-step analysis"
}}

Choose from the available cocktails list only."""

            # Make AI call with proper formatting for Claude
            body = json.dumps({
                "anthropic_version": "bedrock-2023-05-31",
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 800,
                "temperature": 0.7
            })
            
            response = self.bedrock_client.invoke_model(
                modelId=self.model_id,
                body=body,
                contentType='application/json'
            )
            
            # Parse response
            result = json.loads(response['body'].read())
            ai_text = result['content'][0]['text']
            
            # Try to parse JSON response
            try:
                clean_text = ai_text.strip()
                if clean_text.startswith('```json'):
                    clean_text = clean_text[7:]
                if clean_text.endswith('```'):
                    clean_text = clean_text[:-3]
                clean_text = clean_text.strip()
                
                ai_response = json.loads(clean_text)
                return ai_response
                
            except json.JSONDecodeError:
                # If JSON parsing fails, extract info manually
                return {
                    "cocktail_name": self.extract_cocktail_name(ai_text),
                    "explanation": ai_text[:200] + "...",
                    "confidence": "Medium",
                    "alternatives": list(self.cocktails.keys())[:2]
                }
                
        except Exception as e:
            print(f"AI recommendation failed: {e}")
            return self.get_fallback_recommendation(movie_info)
    
    def extract_cocktail_name(self, text: str) -> str:
        """Extract cocktail name from AI text"""
        text_lower = text.lower()
        for cocktail_name in self.cocktails.keys():
            if cocktail_name in text_lower:
                return cocktail_name
        return 'martini'  # Default fallback
    
    def get_fallback_recommendation(self, movie_info: Dict) -> Dict:
        """Intelligent fallback when AI fails"""
        genre = movie_info.get('genre', '').lower()
        year = movie_info.get('year', '')
        
        # Rule-based recommendations
        if 'romance' in genre or 'drama' in genre:
            cocktail = 'martini'
            explanation = "A sophisticated Martini complements the emotional depth and elegance of this romantic drama."
        elif 'action' in genre or 'thriller' in genre:
            cocktail = 'old_fashioned'
            explanation = "An Old Fashioned's bold character matches the intensity and strength of this action-packed film."
        elif 'comedy' in genre:
            cocktail = 'margarita'
            explanation = "A fun, refreshing Margarita enhances the light-hearted and entertaining nature of this comedy."
        elif year and int(year) < 1970:
            cocktail = 'manhattan'
            explanation = "A classic Manhattan perfectly captures the sophisticated atmosphere of this vintage film."
        else:
            cocktail = 'negroni'
            explanation = "A complex Negroni offers the perfect balance of sophistication for this unique cinematic experience."
        
        return {
            "cocktail_name": cocktail,
            "explanation": explanation,
            "confidence": "Medium",
            "alternatives": [name for name in self.cocktails.keys() if name != cocktail][:2]
        }
    
    def find_cocktail(self, cocktail_name: str) -> Optional[Dict]:
        """Find cocktail in database"""
        if not cocktail_name:
            return None
            
        cocktail_key = cocktail_name.lower().replace(' ', '_')
        return self.cocktails.get(cocktail_key)
    
    def sync_recommend(self, movie_title: str) -> Dict:
        """Synchronous version for easy testing"""
        return asyncio.run(self.get_cocktail_for_movie(movie_title))


async def run_demo():
    """Run the interactive demo"""
    print("🎬🍸 AI Movie & Cocktail Pairing Demo")
    print("="*50)
    
    agent = MovieCocktailAgent()
    
    # Test movies
    test_movies = [
        "Casablanca",
        "Blade Runner 2049", 
        "Her",
        "The Godfather",
        "Pulp Fiction"
    ]
    
    for movie in test_movies:
        print(f"\n🎬 Movie: {movie}")
        print("-" * 40)
        
        result = await agent.get_cocktail_for_movie(movie)
        
        if result['success']:
            print(f"🍸 Recommended Cocktail: {result['cocktail']['name']}")
            print(f"🥃 Glass: {result['cocktail']['glass']}")
            print(f"🍋 Ingredients: {', '.join(result['cocktail']['ingredients'])}")
            print(f"💭 Why: {result['explanation']}")
            print(f"🎯 Confidence: {result['confidence']}")
            
            if result['alternatives']:
                print(f"🔄 Alternatives: {', '.join(result['alternatives'])}")
        else:
            print(f"❌ Error: {result['error']}")
    
    print(f"\n{'='*50}")
    print("🎉 Demo Complete! Your AI system is working!")

def interactive_demo():
    """Interactive mode for testing"""
    print("🎬🍸 Interactive Movie & Cocktail Pairing")
    print("Type 'quit' to exit")
    print("-" * 40)
    
    agent = MovieCocktailAgent()
    
    while True:
        movie = input("\nEnter a movie title: ").strip()
        if movie.lower() in ['quit', 'exit', 'q']:
            break
            
        if not movie:
            print("Please enter a movie title!")
            continue
            
        print(f"🤔 Thinking about {movie}...")
        result = agent.sync_recommend(movie)
        
        if result['success']:
            print(f"\n🎬 Movie: {result['movie']['title']} ({result['movie']['year']})")
            print(f"🎭 Genre: {result['movie']['genre']}")
            print(f"🍸 Perfect Cocktail: {result['cocktail']['name']}")
            print(f"🥃 Served in: {result['cocktail']['glass']}")
            print(f"💭 Why this pairing: {result['explanation']}")
        else:
            print(f"❌ Error: {result['error']}")
    
    print("Thanks for testing! 🎉")

if __name__ == "__main__":
    print("Choose demo mode:")
    print("1. Auto demo (recommended)")
    print("2. Interactive mode")
    
    choice = input("Enter choice (1 or 2): ").strip()
    
    if choice == "2":
        interactive_demo()
    else:
        asyncio.run(run_demo())
