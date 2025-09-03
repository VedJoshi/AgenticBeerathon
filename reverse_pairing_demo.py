#!/usr/bin/env python3
"""
🍸🎬 Reverse Pairing Agent: Alcohol → Movie Recommendations
AI agent that recommends movies based on alcohol preferences
"""

import asyncio
import sys
import os
from typing import Dict, Optional, List
import json
import boto3
from dotenv import load_dotenv

# Load environment
load_dotenv()

class ReversePairingAgent:
    """AI agent that recommends movies based on alcohol preferences"""
    
    def __init__(self):
        self.setup_aws()
        self.load_alcohol_data()
        self.load_movie_database()
        
    def setup_aws(self):
        """Initialize AWS Bedrock client"""
        try:
            self.bedrock_client = boto3.client(
                'bedrock-runtime',
                region_name=os.getenv('AWS_REGION', 'us-east-1')
            )
            self.model_id = os.getenv('BEDROCK_MODEL_ID', 'anthropic.claude-3-sonnet-20240229-v1:0')
            print("🎬 Reverse Pairing Agent initialized with AWS Bedrock!")
        except Exception as e:
            print(f"⚠️ AWS Bedrock initialization failed: {str(e)}")
            self.bedrock_client = None
            
    def load_alcohol_data(self):
        """Load alcohol database (cocktails, beer, wine)"""
        # Cocktails
        self.cocktails = {
            'martini': {
                'name': 'Martini',
                'type': 'cocktail',
                'ingredients': ['gin', 'dry vermouth', 'olive'],
                'glass': 'martini glass',
                'category': 'classic',
                'tags': ['elegant', 'strong', 'sophisticated', 'formal'],
                'flavor_profile': 'crisp, botanical, dry',
                'occasion': 'elegant evening, business dinner'
            },
            'old_fashioned': {
                'name': 'Old Fashioned',
                'type': 'cocktail',
                'ingredients': ['whiskey', 'sugar', 'bitters', 'orange'],
                'glass': 'rocks glass',
                'category': 'classic',
                'tags': ['traditional', 'strong', 'bitter', 'masculine'],
                'flavor_profile': 'rich, sweet, bitter, warming',
                'occasion': 'contemplative evening, cigar lounge'
            },
            'negroni': {
                'name': 'Negroni',
                'type': 'cocktail',
                'ingredients': ['gin', 'campari', 'sweet vermouth'],
                'glass': 'rocks glass',
                'category': 'bitter',
                'tags': ['bitter', 'sophisticated', 'italian', 'complex'],
                'flavor_profile': 'bitter, herbal, complex, aperitif',
                'occasion': 'aperitivo hour, intellectual discussion'
            },
            'margarita': {
                'name': 'Margarita',
                'type': 'cocktail',
                'ingredients': ['tequila', 'lime juice', 'triple sec'],
                'glass': 'margarita glass',
                'category': 'tropical',
                'tags': ['citrus', 'refreshing', 'party', 'festive'],
                'flavor_profile': 'tart, citrusy, refreshing, energizing',
                'occasion': 'beach party, celebration, summer evening'
            },
            'manhattan': {
                'name': 'Manhattan',
                'type': 'cocktail',
                'ingredients': ['whiskey', 'sweet vermouth', 'bitters'],
                'glass': 'coupe glass',
                'category': 'classic',
                'tags': ['sophisticated', 'strong', 'traditional', 'urban'],
                'flavor_profile': 'rich, smooth, slightly sweet, warming',
                'occasion': 'city nightlife, jazz club, intimate dinner'
            }
        }
        
        # Beers (sample)
        self.beers = {
            'ipa': {
                'name': 'IPA (India Pale Ale)',
                'type': 'beer',
                'style': 'IPA',
                'abv': '5.5-7.5%',
                'tags': ['hoppy', 'bitter', 'citrusy', 'bold'],
                'flavor_profile': 'hoppy, bitter, citrus, floral',
                'occasion': 'casual evening, sports bar, brewery'
            },
            'stout': {
                'name': 'Stout',
                'type': 'beer',
                'style': 'Stout',
                'abv': '4-7%',
                'tags': ['dark', 'roasted', 'creamy', 'rich'],
                'flavor_profile': 'coffee, chocolate, roasted, creamy',
                'occasion': 'cozy pub, winter evening, contemplative mood'
            }
        }
        
        # Wines (sample)
        self.wines = {
            'cabernet_sauvignon': {
                'name': 'Cabernet Sauvignon',
                'type': 'wine',
                'color': 'red',
                'body': 'full',
                'tags': ['bold', 'tannic', 'sophisticated', 'food-pairing'],
                'flavor_profile': 'blackcurrant, cedar, vanilla, full-bodied',
                'occasion': 'fine dining, romantic dinner, special occasion'
            },
            'chardonnay': {
                'name': 'Chardonnay',
                'type': 'wine',
                'color': 'white',
                'body': 'medium-full',
                'tags': ['versatile', 'buttery', 'oak', 'elegant'],
                'flavor_profile': 'apple, vanilla, butter, oak',
                'occasion': 'dinner party, business lunch, relaxed evening'
            }
        }
        
        # Combine all alcohol types
        self.all_alcohol = {**self.cocktails, **self.beers, **self.wines}
        print(f"✅ Loaded {len(self.all_alcohol)} alcoholic beverages")
        
    def load_movie_database(self):
        """Load movie database for recommendations"""
        self.movies = {
            # Classic/Sophisticated films
            'casablanca': {
                'title': 'Casablanca',
                'year': 1942,
                'genre': ['Drama', 'Romance', 'War'],
                'mood': ['sophisticated', 'romantic', 'classic'],
                'setting': ['1940s', 'Morocco', 'wartime'],
                'themes': ['love', 'sacrifice', 'morality']
            },
            'the_godfather': {
                'title': 'The Godfather',
                'year': 1972,
                'genre': ['Crime', 'Drama'],
                'mood': ['dark', 'powerful', 'traditional'],
                'setting': ['1940s-50s', 'New York', 'family'],
                'themes': ['power', 'family', 'tradition']
            },
            
            # Modern sophisticated
            'blade_runner_2049': {
                'title': 'Blade Runner 2049',
                'year': 2017,
                'genre': ['Sci-Fi', 'Drama', 'Thriller'],
                'mood': ['contemplative', 'complex', 'atmospheric'],
                'setting': ['future', 'urban', 'dystopian'],
                'themes': ['humanity', 'identity', 'technology']
            },
            'her': {
                'title': 'Her',
                'year': 2013,
                'genre': ['Drama', 'Romance', 'Sci-Fi'],
                'mood': ['melancholic', 'intimate', 'thoughtful'],
                'setting': ['near-future', 'urban', 'minimalist'],
                'themes': ['love', 'loneliness', 'technology']
            },
            
            # Bold/Action
            'pulp_fiction': {
                'title': 'Pulp Fiction',
                'year': 1994,
                'genre': ['Crime', 'Drama'],
                'mood': ['edgy', 'stylish', 'bold'],
                'setting': ['1990s', 'Los Angeles', 'urban'],
                'themes': ['violence', 'redemption', 'style']
            },
            'mad_max_fury_road': {
                'title': 'Mad Max: Fury Road',
                'year': 2015,
                'genre': ['Action', 'Adventure', 'Sci-Fi'],
                'mood': ['intense', 'adrenaline', 'bold'],
                'setting': ['post-apocalyptic', 'desert', 'survival'],
                'themes': ['survival', 'freedom', 'rebellion']
            },
            
            # Light/Fun
            'grand_budapest_hotel': {
                'title': 'The Grand Budapest Hotel',
                'year': 2014,
                'genre': ['Comedy', 'Drama', 'Adventure'],
                'mood': ['whimsical', 'elegant', 'charming'],
                'setting': ['1930s', 'Europe', 'hotel'],
                'themes': ['friendship', 'nostalgia', 'style']
            },
            'amelie': {
                'title': 'Amélie',
                'year': 2001,
                'genre': ['Comedy', 'Romance'],
                'mood': ['whimsical', 'charming', 'romantic'],
                'setting': ['Paris', 'contemporary', 'artistic'],
                'themes': ['love', 'kindness', 'imagination']
            }
        }
        print(f"✅ Loaded {len(self.movies)} movies for recommendations")
    
    async def recommend_movies_for_alcohol(self, alcohol_name: str) -> Dict:
        """Get AI-powered movie recommendations for a given alcohol"""
        try:
            # Step 1: Find the alcohol
            alcohol = self.find_alcohol(alcohol_name)
            if not alcohol:
                return {
                    'success': False,
                    'error': f"Alcohol '{alcohol_name}' not found",
                    'alcohol': None,
                    'movies': [],
                    'explanation': None
                }
            
            # Step 2: Use AI to analyze alcohol and recommend movies
            ai_response = await self.get_ai_movie_recommendations(alcohol)
            
            # Step 3: Get detailed movie info for recommendations
            recommended_movies = []
            for movie_key in ai_response.get('movie_recommendations', [])[:3]:
                movie_info = self.find_movie(movie_key)
                if movie_info:
                    recommended_movies.append(movie_info)
            
            return {
                'success': True,
                'alcohol': {
                    'name': alcohol['name'],
                    'type': alcohol['type'],
                    'flavor_profile': alcohol.get('flavor_profile', ''),
                    'tags': alcohol.get('tags', []),
                    'occasion': alcohol.get('occasion', '')
                },
                'movies': recommended_movies,
                'explanation': ai_response.get('explanation', ''),
                'mood_analysis': ai_response.get('mood_analysis', ''),
                'pairing_strength': ai_response.get('confidence', 'Medium')
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f"Error generating movie recommendations: {str(e)}",
                'alcohol': None,
                'movies': [],
                'explanation': None
            }
    
    def find_alcohol(self, alcohol_name: str) -> Optional[Dict]:
        """Find alcohol by name"""
        alcohol_lower = alcohol_name.lower().replace(' ', '_')
        
        # Direct match
        if alcohol_lower in self.all_alcohol:
            return self.all_alcohol[alcohol_lower]
        
        # Partial match search
        for name, alcohol in self.all_alcohol.items():
            if (alcohol_lower in name.lower() or 
                name.lower() in alcohol_lower or
                alcohol_lower in alcohol['name'].lower()):
                return alcohol
        
        return None
    
    def find_movie(self, movie_identifier: str) -> Optional[Dict]:
        """Find movie by title or key"""
        movie_lower = movie_identifier.lower().replace(' ', '_').replace(':', '')
        
        # Direct key match
        if movie_lower in self.movies:
            return self.movies[movie_lower]
        
        # Search by title
        for key, movie in self.movies.items():
            if (movie_lower in movie['title'].lower().replace(' ', '_') or
                movie['title'].lower().replace(' ', '_') in movie_lower):
                return movie
        
        return None
    
    async def get_ai_movie_recommendations(self, alcohol: Dict) -> Dict:
        """Use AI to recommend movies based on alcohol characteristics"""
        
        if not self.bedrock_client:
            return self.get_intelligent_fallback_movies(alcohol)
        
        try:
            # Create comprehensive AI prompt
            prompt = f"""You are an expert sommelier and film critic who specializes in pairing movies with alcoholic beverages.

ALCOHOL TO ANALYZE:
Name: {alcohol['name']}
Type: {alcohol['type']}
Flavor Profile: {alcohol.get('flavor_profile', 'Complex')}
Tags: {', '.join(alcohol.get('tags', []))}
Occasion: {alcohol.get('occasion', 'Evening enjoyment')}

AVAILABLE MOVIES: {', '.join([movie['title'] for movie in self.movies.values()])}

TASK: Recommend movies that would pair perfectly with this drink.

Consider the alcohol's characteristics:
1. Flavor profile (bitter, sweet, complex, light, bold)
2. Sophistication level and cultural associations  
3. Drinking occasion and mood it evokes
4. Historical context and social setting
5. The experience it creates (relaxing, energizing, contemplative)

Match these with films that have complementary:
- Atmosphere and mood
- Visual aesthetics  
- Themes and character sophistication
- Historical period or cultural context
- Viewing experience (intense, relaxing, thought-provoking)

Respond with a JSON object:
{{
    "movie_recommendations": ["Movie Title 1", "Movie Title 2", "Movie Title 3"],
    "explanation": "Detailed explanation of why these movies pair with this drink (2-3 sentences)",
    "mood_analysis": "Analysis of how the alcohol's mood connects to the film atmospheres",
    "confidence": "High/Medium/Low confidence in this pairing",
    "reasoning": "Step-by-step reasoning for the movie selection"
}}

Focus on meaningful connections between the drink's character and the films' atmospheres."""

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
                    "movie_recommendations": self.extract_movies_from_text(ai_text),
                    "explanation": ai_text[:300] + "...",
                    "mood_analysis": "AI provided detailed analysis",
                    "confidence": "Medium",
                    "reasoning": "AI analysis with manual parsing"
                }
                
        except Exception as e:
            print(f"AI recommendation failed: {str(e)}")
            return self.get_intelligent_fallback_movies(alcohol)
    
    def extract_movies_from_text(self, text: str) -> List[str]:
        """Extract movie titles from AI text response"""
        # Look for movie titles that match our database
        found_movies = []
        for movie in self.movies.values():
            if movie['title'].lower() in text.lower():
                found_movies.append(movie['title'])
        
        if found_movies:
            return found_movies[:3]
        else:
            # Fallback to first 3 movies
            return [list(self.movies.values())[i]['title'] for i in range(3)]
    
    def get_intelligent_fallback_movies(self, alcohol: Dict) -> Dict:
        """Intelligent rule-based movie recommendations when AI fails"""
        name = alcohol['name'].lower()
        alcohol_type = alcohol['type']
        tags = [tag.lower() for tag in alcohol.get('tags', [])]
        
        # Rule-based movie matching
        if 'sophisticated' in tags or 'elegant' in tags:
            movies = ["Casablanca", "The Godfather", "Blade Runner 2049"]
            explanation = f"The sophisticated character of {alcohol['name']} pairs with classic and thoughtful cinema."
            
        elif 'bitter' in tags or 'complex' in tags:
            movies = ["Blade Runner 2049", "Her", "Pulp Fiction"]
            explanation = f"The complex, nuanced flavors of {alcohol['name']} match films with depth and moral complexity."
            
        elif 'bold' in tags or 'intense' in tags:
            movies = ["Mad Max: Fury Road", "Pulp Fiction", "The Godfather"]
            explanation = f"The bold character of {alcohol['name']} complements powerful, intense cinema."
            
        elif 'party' in tags or 'festive' in tags:
            movies = ["The Grand Budapest Hotel", "Amélie", "Pulp Fiction"]
            explanation = f"The lively, festive spirit of {alcohol['name']} enhances entertaining and stylish films."
            
        elif alcohol_type == 'wine':
            movies = ["Casablanca", "The Grand Budapest Hotel", "Her"]
            explanation = f"The refined elegance of {alcohol['name']} pairs beautifully with sophisticated, character-driven films."
            
        elif alcohol_type == 'beer':
            movies = ["Mad Max: Fury Road", "Pulp Fiction", "The Godfather"]
            explanation = f"The approachable yet complex character of {alcohol['name']} matches films with strong storytelling."
            
        else:
            movies = ["Her", "Blade Runner 2049", "Amélie"]
            explanation = f"The unique character of {alcohol['name']} complements thoughtful, atmospheric cinema."
        
        return {
            "movie_recommendations": movies,
            "explanation": explanation,
            "mood_analysis": f"The {alcohol['name']} suggests pairing with films that match its sophistication and mood",
            "confidence": "Medium",
            "reasoning": "Rule-based selection using alcohol characteristics"
        }
    
    def sync_recommend_movies(self, alcohol_name: str) -> Dict:
        """Synchronous version for easy testing"""
        return asyncio.run(self.recommend_movies_for_alcohol(alcohol_name))


async def run_reverse_demo():
    """Run the reverse pairing demo"""
    print("🍸🎬 AI Alcohol → Movie Pairing Demo")
    print("="*50)
    
    agent = ReversePairingAgent()
    
    # Test alcohols
    test_alcohols = [
        "Negroni",
        "Old Fashioned", 
        "Margarita",
        "Martini",
        "IPA",
        "Cabernet Sauvignon"
    ]
    
    for alcohol in test_alcohols:
        print(f"\n🍸 Alcohol: {alcohol}")
        print("-" * 40)
        
        result = await agent.recommend_movies_for_alcohol(alcohol)
        
        if result['success']:
            print(f"🥃 Type: {result['alcohol']['type']}")
            print(f"👅 Flavor: {result['alcohol']['flavor_profile']}")
            print(f"🏷️ Tags: {', '.join(result['alcohol']['tags'][:3])}")
            print(f"\n🎬 AI Movie Recommendations:")
            
            for i, movie in enumerate(result['movies'], 1):
                print(f"   {i}. {movie['title']} ({movie['year']}) - {'/'.join(movie['genre'])}")
            
            print(f"\n💭 Why These Movies:")
            print(f"   {result['explanation'][:200]}...")
            
            print(f"\n🎯 Confidence: {result['pairing_strength']}")
            
        else:
            print(f"❌ Error: {result['error']}")
    
    print(f"\n{'='*50}")
    print("🎉 Reverse Pairing Demo Complete!")

def interactive_reverse_demo():
    """Interactive alcohol → movie demo"""
    print("🍸🎬 Interactive Alcohol → Movie Pairing")
    print("Type 'quit' to exit")
    print("-" * 40)
    
    agent = ReversePairingAgent()
    
    while True:
        alcohol = input("\nEnter alcohol name (e.g., Negroni, IPA, Chardonnay): ").strip()
        if alcohol.lower() in ['quit', 'exit', 'q']:
            break
            
        if not alcohol:
            print("Please enter an alcohol name!")
            continue
            
        print(f"🤔 Thinking about {alcohol}...")
        result = agent.sync_recommend_movies(alcohol)
        
        if result['success']:
            print(f"\n🍸 Alcohol: {result['alcohol']['name']} ({result['alcohol']['type']})")
            print(f"👅 Flavor Profile: {result['alcohol']['flavor_profile']}")
            print(f"🎬 Perfect Movies:")
            
            for i, movie in enumerate(result['movies'], 1):
                print(f"   {i}. {movie['title']} ({movie['year']})")
                print(f"      Genre: {'/'.join(movie['genre'])}")
            
            print(f"\n💭 Why this pairing: {result['explanation']}")
        else:
            print(f"❌ Error: {result['error']}")
    
    print("Thanks for testing the reverse pairing! 🎉")

if __name__ == "__main__":
    print("Choose reverse demo mode:")
    print("1. Auto demo (recommended)")
    print("2. Interactive mode")
    
    choice = input("Enter choice (1 or 2): ").strip()
    
    if choice == "2":
        interactive_reverse_demo()
    else:
        asyncio.run(run_reverse_demo())
