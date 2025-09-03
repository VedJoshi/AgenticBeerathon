#!/usr/bin/env python3
"""
🚀 Improved LLM API Demo
Robust AI-powered movie & cocktail recommendations with better error handling
"""

import asyncio
import os
import sys
import json
import re
from typing import Dict, Optional, List
import boto3
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class ImprovedLLMAgent:
    """Improved AI agent with robust LLM API calls"""
    
    def __init__(self):
        self.setup_aws()
        self.setup_data()
        
    def setup_aws(self):
        """Initialize AWS Bedrock client with better error handling"""
        try:
            self.bedrock_client = boto3.client(
                'bedrock-runtime',
                region_name=os.getenv('AWS_REGION', 'us-east-1'),
                aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
                aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
            )
            self.model_id = os.getenv('BEDROCK_MODEL_ID', 'anthropic.claude-3-sonnet-20240229-v1:0')
            
            # Test the connection
            self.test_aws_connection()
            print("✅ AWS Bedrock initialized and tested successfully!")
            
        except Exception as e:
            print(f"❌ AWS Bedrock initialization failed: {e}")
            self.bedrock_client = None
            
    def test_aws_connection(self):
        """Test AWS connection with a simple call"""
        if not self.bedrock_client:
            raise Exception("No Bedrock client")
            
        # Simple test call
        test_body = json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "messages": [{"role": "user", "content": "Hello, respond with just 'OK'"}],
            "max_tokens": 10,
            "temperature": 0.1
        })
        
        response = self.bedrock_client.invoke_model(
            modelId=self.model_id,
            body=test_body,
            contentType='application/json'
        )
        
        result = json.loads(response['body'].read())
        if 'content' not in result:
            raise Exception("Invalid response format")
            
    def setup_data(self):
        """Setup cocktail and movie data"""
        self.cocktails = {
            'martini': {
                'name': 'Martini',
                'ingredients': ['gin', 'dry vermouth', 'olive'],
                'glass': 'martini glass',
                'category': 'classic',
                'description': 'The epitome of sophistication',
                'strength': 'strong',
                'flavor_profile': ['dry', 'crisp', 'herbal']
            },
            'old_fashioned': {
                'name': 'Old Fashioned',
                'ingredients': ['whiskey', 'sugar', 'bitters', 'orange'],
                'glass': 'rocks glass',
                'category': 'classic',
                'description': 'A timeless whiskey cocktail',
                'strength': 'strong',
                'flavor_profile': ['sweet', 'bitter', 'woody']
            },
            'negroni': {
                'name': 'Negroni',
                'ingredients': ['gin', 'campari', 'sweet vermouth'],
                'glass': 'rocks glass',
                'category': 'bitter',
                'description': 'Bold and complex Italian aperitif',
                'strength': 'medium',
                'flavor_profile': ['bitter', 'herbal', 'complex']
            },
            'manhattan': {
                'name': 'Manhattan',
                'ingredients': ['whiskey', 'sweet vermouth', 'bitters'],
                'glass': 'coupe glass',
                'category': 'classic',
                'description': 'Sophisticated and smooth',
                'strength': 'strong',
                'flavor_profile': ['rich', 'smooth', 'sophisticated']
            },
            'margarita': {
                'name': 'Margarita',
                'ingredients': ['tequila', 'lime juice', 'triple sec'],
                'glass': 'margarita glass',
                'category': 'tropical',
                'description': 'Refreshing citrus celebration',
                'strength': 'medium',
                'flavor_profile': ['citrus', 'refreshing', 'bright']
            }
        }
        
        self.movies = {
            'casablanca': {
                'title': 'Casablanca',
                'year': '1942',
                'genre': 'Drama, Romance, War',
                'director': 'Michael Curtiz',
                'plot': 'A cynical American expatriate struggles to decide whether to help his former lover and her fugitive husband escape French Morocco.',
                'imdb_rating': '8.5',
                'mood': 'romantic, nostalgic, sophisticated'
            },
            'blade runner 2049': {
                'title': 'Blade Runner 2049',
                'year': '2017',
                'genre': 'Action, Drama, Mystery',
                'director': 'Denis Villeneuve',
                'plot': 'A young blade runner discovers a secret that could end replicant slavery.',
                'imdb_rating': '8.0',
                'mood': 'dark, contemplative, futuristic'
            },
            'the godfather': {
                'title': 'The Godfather',
                'year': '1972',
                'genre': 'Crime, Drama',
                'director': 'Francis Ford Coppola',
                'plot': 'The aging patriarch of an organized crime dynasty transfers control to his reluctant son.',
                'imdb_rating': '9.2',
                'mood': 'intense, sophisticated, dramatic'
            }
        }
        
        print(f"✅ Loaded {len(self.cocktails)} cocktails and {len(self.movies)} movies")
    
    async def get_ai_recommendation(self, movie_title: str) -> Dict:
        """Get AI recommendation with improved error handling"""
        
        # Get movie info
        movie_info = self.get_movie_info(movie_title)
        
        if not self.bedrock_client:
            print("⚠️ Using fallback recommendations (no AWS connection)")
            return self.get_smart_fallback(movie_info)
        
        try:
            # Create comprehensive prompt
            prompt = self.create_detailed_prompt(movie_info)
            
            # Make AI call with proper error handling
            ai_response = await self.call_claude_api(prompt)
            
            # Parse and validate response
            parsed_response = self.parse_ai_response(ai_response)
            
            # Enhance with cocktail details
            cocktail_details = self.get_cocktail_details(parsed_response['cocktail_name'])
            
            return {
                'success': True,
                'movie': movie_info,
                'cocktail': cocktail_details,
                'explanation': parsed_response['explanation'],
                'confidence': parsed_response['confidence'],
                'alternatives': parsed_response['alternatives'],
                'ai_reasoning': parsed_response.get('reasoning', ''),
                'source': 'AI'
            }
            
        except Exception as e:
            print(f"🔄 AI call failed ({str(e)}), using smart fallback")
            fallback = self.get_smart_fallback(movie_info)
            fallback['source'] = 'Fallback'
            return fallback
    
    def create_detailed_prompt(self, movie_info: Dict) -> str:
        """Create a detailed, structured prompt for Claude"""
        
        cocktail_list = []
        for name, details in self.cocktails.items():
            cocktail_list.append(f"- {details['name']}: {details['description']} (Flavors: {', '.join(details['flavor_profile'])})")
        
        prompt = f"""You are a world-renowned sommelier and film critic. Your expertise lies in creating perfect cocktail pairings for movies.

🎬 MOVIE TO ANALYZE:
Title: {movie_info['title']}
Year: {movie_info['year']}
Genre: {movie_info['genre']}
Director: {movie_info['director']}
Plot: {movie_info['plot']}
Mood: {movie_info.get('mood', 'Unknown')}
IMDB Rating: {movie_info['imdb_rating']}

🍸 AVAILABLE COCKTAILS:
{chr(10).join(cocktail_list)}

🎯 YOUR TASK:
Analyze this movie's atmosphere, themes, setting, and emotional tone. Then recommend the ONE cocktail that would create the most perfect pairing experience.

Consider these factors:
1. Movie's historical period and cultural setting
2. Emotional atmosphere (romantic, tense, mysterious, etc.)
3. Character sophistication and social class
4. Visual aesthetics and cinematography style
5. Intended viewing experience and mood enhancement

🔍 RESPOND EXACTLY IN THIS JSON FORMAT:
{{
    "cocktail_name": "exact_name_from_list",
    "explanation": "2-3 sentences explaining why this pairing works perfectly",
    "confidence": "High",
    "alternatives": ["second_choice", "third_choice"],
    "reasoning": "Step-by-step analysis of your decision"
}}

Important: Use ONLY cocktail names from the provided list. Be specific and confident in your recommendation."""

        return prompt
    
    async def call_claude_api(self, prompt: str, max_retries: int = 3) -> str:
        """Make API call to Claude with retries"""
        
        for attempt in range(max_retries):
            try:
                body = json.dumps({
                    "anthropic_version": "bedrock-2023-05-31",
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": 1000,
                    "temperature": 0.7,
                    "top_p": 0.9
                })
                
                response = self.bedrock_client.invoke_model(
                    modelId=self.model_id,
                    body=body,
                    contentType='application/json'
                )
                
                result = json.loads(response['body'].read())
                
                if 'content' in result and len(result['content']) > 0:
                    return result['content'][0]['text']
                else:
                    raise Exception("Invalid response format")
                    
            except Exception as e:
                print(f"   Attempt {attempt + 1} failed: {str(e)}")
                if attempt == max_retries - 1:
                    raise e
                await asyncio.sleep(1)  # Wait before retry
        
        raise Exception("All API attempts failed")
    
    def parse_ai_response(self, ai_text: str) -> Dict:
        """Parse AI response with multiple fallback strategies"""
        
        # Strategy 1: Try to parse as JSON
        json_response = self.extract_json_from_text(ai_text)
        if json_response:
            return self.validate_ai_response(json_response)
        
        # Strategy 2: Extract information using regex patterns
        return self.extract_info_with_regex(ai_text)
    
    def extract_json_from_text(self, text: str) -> Optional[Dict]:
        """Extract JSON from text with multiple strategies"""
        
        # Clean the text
        text = text.strip()
        
        # Remove markdown formatting
        if text.startswith('```json'):
            text = text[7:]
        if text.startswith('```'):
            text = text[3:]
        if text.endswith('```'):
            text = text[:-3]
        
        text = text.strip()
        
        # Try to find JSON block
        json_patterns = [
            r'\{[^{}]*\}',  # Simple JSON object
            r'\{.*\}',      # Any JSON object
        ]
        
        for pattern in json_patterns:
            matches = re.findall(pattern, text, re.DOTALL)
            for match in matches:
                try:
                    return json.loads(match)
                except json.JSONDecodeError:
                    continue
        
        # Try parsing the whole text
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            return None
    
    def extract_info_with_regex(self, text: str) -> Dict:
        """Extract information using regex when JSON parsing fails"""
        
        # Extract cocktail name
        cocktail_name = None
        for name in self.cocktails.keys():
            if name.lower() in text.lower() or self.cocktails[name]['name'].lower() in text.lower():
                cocktail_name = name
                break
        
        if not cocktail_name:
            cocktail_name = 'martini'  # Default
        
        # Extract explanation (first sentence or paragraph)
        explanation_match = re.search(r'[.!?]\s*([^.!?]+[.!?])', text)
        explanation = explanation_match.group(1) if explanation_match else text[:200] + "..."
        
        return {
            'cocktail_name': cocktail_name,
            'explanation': explanation,
            'confidence': 'Medium',
            'alternatives': [name for name in self.cocktails.keys() if name != cocktail_name][:2],
            'reasoning': 'Extracted from AI text response'
        }
    
    def validate_ai_response(self, response: Dict) -> Dict:
        """Validate and clean AI response"""
        
        # Ensure cocktail name is valid
        cocktail_name = response.get('cocktail_name', '').lower().replace(' ', '_')
        if cocktail_name not in self.cocktails:
            # Try to find close match
            for name in self.cocktails.keys():
                if name in cocktail_name or cocktail_name in name:
                    cocktail_name = name
                    break
            else:
                cocktail_name = 'martini'  # Default fallback
        
        # Ensure alternatives are valid
        alternatives = response.get('alternatives', [])
        valid_alternatives = []
        for alt in alternatives:
            alt_clean = alt.lower().replace(' ', '_')
            if alt_clean in self.cocktails and alt_clean != cocktail_name:
                valid_alternatives.append(alt_clean)
        
        # Add more alternatives if needed
        while len(valid_alternatives) < 2:
            for name in self.cocktails.keys():
                if name != cocktail_name and name not in valid_alternatives:
                    valid_alternatives.append(name)
                    break
            break
        
        return {
            'cocktail_name': cocktail_name,
            'explanation': response.get('explanation', 'Perfect pairing selected by AI'),
            'confidence': response.get('confidence', 'Medium'),
            'alternatives': valid_alternatives[:2],
            'reasoning': response.get('reasoning', 'AI analysis')
        }
    
    def get_movie_info(self, movie_title: str) -> Dict:
        """Get movie information with fallback"""
        movie_key = movie_title.lower()
        
        if movie_key in self.movies:
            return self.movies[movie_key]
        
        # Return generic movie info
        return {
            'title': movie_title,
            'year': 'Unknown',
            'genre': 'Unknown',
            'director': 'Unknown',
            'plot': f'A movie titled "{movie_title}"',
            'imdb_rating': 'N/A',
            'mood': 'varied'
        }
    
    def get_cocktail_details(self, cocktail_name: str) -> Dict:
        """Get detailed cocktail information"""
        return self.cocktails.get(cocktail_name, self.cocktails['martini'])
    
    def get_smart_fallback(self, movie_info: Dict) -> Dict:
        """Intelligent fallback recommendations"""
        genre = movie_info.get('genre', '').lower()
        year = movie_info.get('year', '')
        mood = movie_info.get('mood', '').lower()
        
        # Smart rule-based selection
        if 'romance' in genre or 'romantic' in mood:
            cocktail = 'manhattan'
            explanation = "The Manhattan's sophisticated blend mirrors the complexity of romantic relationships in classic cinema."
        elif 'action' in genre or 'crime' in genre:
            cocktail = 'old_fashioned'
            explanation = "An Old Fashioned's bold character matches the intensity and strength required for action-packed storytelling."
        elif 'mystery' in genre or 'dark' in mood:
            cocktail = 'negroni'
            explanation = "The Negroni's bitter complexity perfectly complements the mysterious and contemplative atmosphere."
        elif year and year.isdigit() and int(year) < 1970:
            cocktail = 'martini'
            explanation = "A classic Martini captures the timeless elegance and sophistication of golden age cinema."
        else:
            cocktail = 'manhattan'
            explanation = "A Manhattan provides the perfect sophisticated backdrop for any great film experience."
        
        cocktail_details = self.get_cocktail_details(cocktail)
        alternatives = [name for name in self.cocktails.keys() if name != cocktail][:2]
        
        return {
            'success': True,
            'movie': movie_info,
            'cocktail': cocktail_details,
            'explanation': explanation,
            'confidence': 'Medium',
            'alternatives': alternatives,
            'ai_reasoning': 'Rule-based intelligent fallback',
            'source': 'Smart Fallback'
        }
    
    def sync_recommend(self, movie_title: str) -> Dict:
        """Synchronous wrapper"""
        return asyncio.run(self.get_ai_recommendation(movie_title))


async def test_improved_llm():
    """Test the improved LLM system"""
    print("🚀 Testing Improved LLM API System")
    print("=" * 60)
    
    agent = ImprovedLLMAgent()
    
    test_movies = [
        "Casablanca",
        "Blade Runner 2049",
        "The Godfather",
        "Pulp Fiction",
        "Inception"
    ]
    
    for movie in test_movies:
        print(f"\n🎬 Testing: {movie}")
        print("-" * 40)
        
        result = await agent.get_ai_recommendation(movie)
        
        if result['success']:
            print(f"🍸 Cocktail: {result['cocktail']['name']}")
            print(f"🥃 Glass: {result['cocktail']['glass']}")
            print(f"🌟 Strength: {result['cocktail']['strength']}")
            print(f"💭 Why: {result['explanation']}")
            print(f"🎯 Confidence: {result['confidence']}")
            print(f"🔄 Alternatives: {', '.join(result['alternatives'])}")
            print(f"🤖 Source: {result['source']}")
            
            if 'ai_reasoning' in result:
                print(f"🧠 AI Reasoning: {result['ai_reasoning'][:100]}...")
        else:
            print(f"❌ Failed: {result.get('error', 'Unknown error')}")
    
    print(f"\n{'=' * 60}")
    print("🎉 LLM Testing Complete!")

def interactive_test():
    """Interactive testing mode"""
    print("🎬🍸 Interactive LLM Testing")
    print("Type 'quit' to exit")
    print("-" * 40)
    
    agent = ImprovedLLMAgent()
    
    while True:
        movie = input("\nEnter movie title: ").strip()
        if movie.lower() in ['quit', 'exit', 'q']:
            break
            
        if not movie:
            continue
            
        print(f"🤔 Processing '{movie}' with AI...")
        result = agent.sync_recommend(movie)
        
        if result['success']:
            print(f"\n✨ Perfect Pairing Found!")
            print(f"🎬 Movie: {result['movie']['title']}")
            print(f"🍸 Cocktail: {result['cocktail']['name']}")
            print(f"💭 Explanation: {result['explanation']}")
            print(f"🤖 Source: {result['source']}")
        else:
            print(f"❌ Error: {result.get('error', 'Unknown error')}")

if __name__ == "__main__":
    print("Choose test mode:")
    print("1. Automated test (recommended)")
    print("2. Interactive test")
    
    choice = input("Enter choice (1 or 2): ").strip()
    
    if choice == "2":
        interactive_test()
    else:
        asyncio.run(test_improved_llm())
