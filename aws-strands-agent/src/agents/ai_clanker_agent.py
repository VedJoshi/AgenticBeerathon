"""
AI-Powered Clanker Agent using AWS Bedrock directly
This version uses real AI to create sophisticated movie-to-cocktail pairings
"""
import asyncio
import sys
import os
from typing import Dict, Optional, List
import json

# AWS imports
import boto3
from botocore.exceptions import NoCredentialsError, ClientError

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.movie_tool import MovieTool
from tools.cocktail_tool import CocktailTool

class AIClankerAgent:
    """AI-powered agent for sophisticated movie-to-cocktail recommendations"""
    
    def __init__(self):
        self.movie_tool = MovieTool()
        self.cocktail_tool = CocktailTool()
        
        # Initialize AWS Bedrock client directly
        try:
            self.bedrock_client = boto3.client(
                'bedrock-runtime',
                region_name=os.getenv('AWS_REGION', 'us-east-1')
            )
            self.model_id = os.getenv('BEDROCK_MODEL_ID', 'anthropic.claude-3-sonnet-20240229-v1:0')
            print("🤖 AI-Powered Clanker Agent initialized with AWS Bedrock!")
        except Exception as e:
            print(f"⚠️ AWS Bedrock initialization failed: {str(e)}")
            print("💡 AI features will use fallback logic")
            self.bedrock_client = None
            self.model_id = None
    
    async def ai_recommend_cocktail_for_movie(self, movie_title: str) -> Dict:
        """
        Get AI-powered cocktail recommendation for a movie
        Uses Claude to analyze movie characteristics and suggest perfect pairings
        """
        try:
            # Step 1: Get movie data
            movie = await self.movie_tool.search_movie(movie_title)
            if not movie:
                return {
                    'success': False,
                    'error': f"Movie '{movie_title}' not found",
                    'movie': None,
                    'cocktail': None,
                    'explanation': None,
                    'alternatives': []
                }
            
            # Step 2: Get a sample of available cocktails for AI to choose from
            available_cocktails = self._get_cocktail_sample()
            
            # Step 3: Use AI to analyze movie and recommend cocktails
            ai_response = await self._get_ai_recommendation(movie, available_cocktails)
            
            # Step 4: Get the recommended cocktail details
            recommended_cocktail = await self._get_cocktail_details(ai_response['primary_recommendation'])
            
            # Step 5: Get alternative recommendations
            alternatives = []
            for alt_name in ai_response.get('alternatives', [])[:2]:  # Limit to 2 alternatives
                alt_cocktail = await self._get_cocktail_details(alt_name)
                if alt_cocktail:
                    alternatives.append(alt_cocktail)
            
            return {
                'success': True,
                'movie': {
                    'title': movie['title'],
                    'year': movie['year'],
                    'genre': movie['genre'],
                    'director': movie['director'],
                    'imdb_rating': movie['imdb_rating'],
                    'plot': movie['plot'][:300] + '...' if len(movie['plot']) > 300 else movie['plot']
                },
                'cocktail': {
                    'name': recommended_cocktail['name'],
                    'ingredients': recommended_cocktail['ingredients'][:6],
                    'instructions': recommended_cocktail['instructions'][:400] + '...' if len(recommended_cocktail['instructions']) > 400 else recommended_cocktail['instructions'],
                    'glass': recommended_cocktail['glass'],
                    'tags': recommended_cocktail.get('tags', [])
                },
                'explanation': ai_response['explanation'],
                'mood_analysis': ai_response.get('mood_analysis', ''),
                'pairing_strength': ai_response.get('confidence', 'High'),
                'alternatives': alternatives,
                'ai_reasoning': ai_response.get('reasoning', '')
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f"AI recommendation error: {str(e)}",
                'movie': None,
                'cocktail': None,
                'explanation': None,
                'alternatives': []
            }
    
    def _get_cocktail_sample(self, sample_size: int = 50) -> List[Dict]:
        """Get a representative sample of cocktails for AI to analyze"""
        try:
            # Get a diverse sample of cocktails from different categories
            all_cocktails = list(self.cocktail_tool._cocktail_cache.values())
            
            # Remove duplicates (some cocktails might be stored multiple ways)
            unique_cocktails = []
            seen_names = set()
            
            for cocktail in all_cocktails:
                name = cocktail.get('name', '').lower()
                if name and name not in seen_names:
                    unique_cocktails.append({
                        'name': cocktail['name'],
                        'ingredients': cocktail['ingredients'][:4],  # First 4 ingredients
                        'category': cocktail.get('category', ''),
                        'tags': cocktail.get('tags', [])[:3],  # First 3 tags
                        'glass': cocktail.get('glass', '')
                    })
                    seen_names.add(name)
                    
                    if len(unique_cocktails) >= sample_size:
                        break
            
            return unique_cocktails[:sample_size]
            
        except Exception as e:
            print(f"Error getting cocktail sample: {str(e)}")
            return []
    
    async def _get_ai_recommendation(self, movie: Dict, available_cocktails: List[Dict]) -> Dict:
        """Use AI to analyze movie and recommend cocktails"""
        
        # Create the AI prompt
        prompt = f"""You are an expert sommelier and film critic who specializes in pairing cocktails with movies. 

MOVIE TO ANALYZE:
Title: {movie['title']} ({movie['year']})
Director: {movie['director']}
Genre: {movie['genre']}
IMDb Rating: {movie['imdb_rating']}
Plot: {movie['plot'][:500]}...

AVAILABLE COCKTAILS:
{json.dumps(available_cocktails[:30], indent=2)}

TASK: Recommend the perfect cocktail pairing for this movie.

Consider:
1. Movie's mood, tone, and atmosphere
2. Time period and setting
3. Character personalities and themes
4. Visual style and cinematography
5. Emotional journey of the film

Respond with a JSON object containing:
{{
    "primary_recommendation": "Exact cocktail name from the list",
    "alternatives": ["Alternative 1", "Alternative 2"],
    "explanation": "Detailed explanation of why this pairing works (2-3 sentences)",
    "mood_analysis": "Brief analysis of the movie's mood and how it connects to the cocktail",
    "confidence": "High/Medium/Low confidence in this pairing",
    "reasoning": "Step-by-step reasoning for the recommendation"
}}

Choose cocktails that exist in the provided list. Focus on creating meaningful connections between the movie's essence and the cocktail's character."""

        try:
            if self.bedrock_client:
                # Call Claude through Bedrock
                response = await self._call_bedrock_async(prompt)
                
                # Parse the JSON response
                response_text = response.strip()
                
                # Extract JSON from the response (in case there's extra text)
                start_idx = response_text.find('{')
                end_idx = response_text.rfind('}') + 1
                
                if start_idx != -1 and end_idx != -1:
                    json_text = response_text[start_idx:end_idx]
                    return json.loads(json_text)
            
            # Fallback if AI is not available
            return self._get_intelligent_fallback(movie, available_cocktails)
                
        except Exception as e:
            print(f"AI recommendation error: {str(e)}")
            return self._get_intelligent_fallback(movie, available_cocktails)
    
    async def _call_bedrock_async(self, prompt: str) -> str:
        """Call AWS Bedrock Claude model asynchronously"""
        try:
            body = json.dumps({
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 1000,
                "temperature": 0.7,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            })
            
            response = self.bedrock_client.invoke_model(
                modelId=self.model_id,
                body=body,
                contentType='application/json'
            )
            
            response_body = json.loads(response['body'].read())
            return response_body['content'][0]['text']
            
        except Exception as e:
            print(f"Bedrock call failed: {str(e)}")
            raise e
    
    def _get_intelligent_fallback(self, movie: Dict, available_cocktails: List[Dict]) -> Dict:
        """Intelligent fallback when AI is not available"""
        genre = movie.get('genre', '').lower()
        year = int(movie.get('year', '2000'))
        rating = float(movie.get('imdb_rating', '7.0'))
        
        # Enhanced genre-based selection
        genre_cocktail_map = {
            'action': ['Whiskey Sour', 'Manhattan', 'Old Fashioned', 'Bourbon Punch'],
            'thriller': ['Vesper Martini', 'Negroni', 'Sazerac', 'Dark \'n\' Stormy'],
            'romance': ['French 75', 'Kir Royale', 'Bellini', 'Champagne Cocktail'],
            'comedy': ['Margarita', 'Mojito', 'Piña Colada', 'Aperol Spritz'],
            'drama': ['Negroni', 'Manhattan', 'Boulevardier', 'Old Fashioned'],
            'horror': ['Blood and Sand', 'Corpse Reviver', 'Zombie', 'Death in the Afternoon'],
            'sci-fi': ['Blue Lagoon', 'Aviation', 'Molecular cocktails', 'Electric Lemonade'],
            'western': ['Whiskey Neat', 'Mint Julep', 'Old Fashioned', 'Bourbon Smash'],
            'musical': ['Champagne Cocktail', 'Sidecar', 'French 75', 'Kir Royale'],
            'war': ['Between the Sheets', 'Corpse Reviver', 'Last Word', 'Army & Navy']
        }
        
        # Find best cocktail match
        preferred_cocktails = []
        for g, cocktails in genre_cocktail_map.items():
            if g in genre:
                preferred_cocktails.extend(cocktails)
        
        # Find matching cocktails from available list
        matches = []
        for cocktail in available_cocktails:
            cocktail_name = cocktail['name']
            if any(pref.lower() in cocktail_name.lower() or cocktail_name.lower() in pref.lower() 
                   for pref in preferred_cocktails):
                matches.append(cocktail)
        
        # Select primary recommendation
        if matches:
            primary = matches[0]
        else:
            # Fallback to sophisticated cocktails for highly rated films
            if rating > 8.0:
                sophisticated = ['Negroni', 'Manhattan', 'Sazerac', 'Boulevardier']
                for cocktail in available_cocktails:
                    if any(soph.lower() in cocktail['name'].lower() for soph in sophisticated):
                        primary = cocktail
                        break
                else:
                    primary = available_cocktails[0] if available_cocktails else {'name': 'Old Fashioned'}
            else:
                primary = available_cocktails[0] if available_cocktails else {'name': 'Old Fashioned'}
        
        # Generate explanation
        era_context = "vintage" if year < 1980 else "modern" if year > 2000 else "classic"
        quality_context = "acclaimed" if rating > 8.0 else "entertaining"
        
        explanation = f"The {primary['name']} perfectly complements this {quality_context} {era_context} film. "
        
        if 'action' in genre:
            explanation += "Its bold character matches the film's intense energy."
        elif 'romance' in genre:
            explanation += "Its elegant profile mirrors the film's romantic sophistication."
        elif 'drama' in genre:
            explanation += "Its complex layers echo the nuanced storytelling."
        else:
            explanation += "The pairing creates a harmonious viewing experience."
        
        return {
            "primary_recommendation": primary['name'],
            "alternatives": [c['name'] for c in matches[1:3]] if len(matches) > 1 else [],
            "explanation": explanation,
            "mood_analysis": f"This {quality_context} {genre} film from {year} deserves a thoughtfully selected cocktail",
            "confidence": "Medium",
            "reasoning": "Enhanced rule-based selection using genre, era, and rating analysis"
        }
    
    async def _get_cocktail_details(self, cocktail_name: str) -> Optional[Dict]:
        """Get full cocktail details by name"""
        try:
            # Search for the cocktail in the local database
            cocktail = await self.cocktail_tool.search_cocktail(cocktail_name)
            if cocktail:
                return cocktail
            
            # Try alternative searches
            name_variations = [
                cocktail_name.lower(),
                cocktail_name.replace(' ', '_').lower(),
                cocktail_name.replace('-', '_').lower()
            ]
            
            for variation in name_variations:
                if variation in self.cocktail_tool._cocktail_cache:
                    return self.cocktail_tool._cocktail_cache[variation]
            
            # If not found, get a random cocktail as fallback
            print(f"Cocktail '{cocktail_name}' not found, using fallback")
            return await self.cocktail_tool.get_random_cocktail()
            
        except Exception as e:
            print(f"Error getting cocktail details for '{cocktail_name}': {str(e)}")
            return await self.cocktail_tool.get_random_cocktail()
    
    def sync_ai_recommend(self, movie_title: str) -> Dict:
        """Synchronous version for easy testing"""
        return asyncio.run(self.ai_recommend_cocktail_for_movie(movie_title))

# Convenience function for quick testing
def quick_ai_recommendation(movie_title: str) -> Dict:
    """Quick AI-powered movie recommendation"""
    agent = AIClankerAgent()
    return agent.sync_ai_recommend(movie_title)

# Test the AI agent if run directly
if __name__ == "__main__":
    print("🤖🎬🍸 AI-Powered Clanker Agent - Testing...")
    
    agent = AIClankerAgent()
    
    # Test cases
    test_movies = [
        "Blade Runner 2049",
        "The Grand Budapest Hotel", 
        "Pulp Fiction"
    ]
    
    for movie in test_movies:
        print(f"\n{'='*60}")
        print(f"🎬 AI Testing: {movie}")
        print('='*60)
        
        result = agent.sync_ai_recommend(movie)
        
        if result['success']:
            print(f"🎬 Movie: {result['movie']['title']} ({result['movie']['year']})")
            print(f"🎭 Genre: {result['movie']['genre']}")
            print(f"⭐ Rating: {result['movie']['imdb_rating']}")
            print(f"\n🤖 AI Mood Analysis:")
            print(f"   {result['mood_analysis']}")
            print(f"\n🍸 AI Recommended: {result['cocktail']['name']}")
            print(f"🥃 Glass: {result['cocktail']['glass']}")
            print(f"🧪 Ingredients: {', '.join(result['cocktail']['ingredients'][:3])}...")
            print(f"\n💭 AI Explanation:")
            print(f"   {result['explanation']}")
            print(f"\n🎯 Pairing Strength: {result['pairing_strength']}")
            
            if result['alternatives']:
                print(f"\n🔄 Alternative Suggestions:")
                for i, alt in enumerate(result['alternatives'], 1):
                    print(f"   {i}. {alt['name']}")
                    
        else:
            print(f"❌ Error: {result['error']}")
    
    print(f"\n{'='*60}")
    print("🎉 AI-Powered Testing Complete!")
    print("Ready for intelligent recommendations! 🚀")
