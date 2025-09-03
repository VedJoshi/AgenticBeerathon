#!/usr/bin/env python3
"""
🎯 Production-Ready LLM API System
Enterprise-grade AI-powered recommendations with bulletproof error handling
"""

import asyncio
import os
import sys
import json
import re
from typing import Dict, Optional, List, Any
import boto3
from dotenv import load_dotenv
import logging
from datetime import datetime

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ProductionLLMAgent:
    """Production-ready AI agent with enterprise-grade error handling"""
    
    def __init__(self):
        self.setup_aws()
        self.setup_data()
        self.api_calls_made = 0
        self.successful_calls = 0
        self.start_time = datetime.now()
        
    def setup_aws(self):
        """Initialize AWS with comprehensive error handling"""
        try:
            # Validate environment variables
            required_vars = ['AWS_ACCESS_KEY_ID', 'AWS_SECRET_ACCESS_KEY']
            missing_vars = [var for var in required_vars if not os.getenv(var)]
            
            if missing_vars:
                logger.warning(f"Missing AWS environment variables: {missing_vars}")
                self.bedrock_client = None
                return
            
            self.bedrock_client = boto3.client(
                'bedrock-runtime',
                region_name=os.getenv('AWS_REGION', 'us-east-1'),
                aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
                aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
            )
            
            self.model_id = os.getenv('BEDROCK_MODEL_ID', 'anthropic.claude-3-sonnet-20240229-v1:0')
            
            # Test connection
            self._test_connection()
            logger.info("✅ AWS Bedrock initialized successfully")
            
        except Exception as e:
            logger.error(f"❌ AWS setup failed: {e}")
            self.bedrock_client = None
    
    def _test_connection(self):
        """Test AWS connection with minimal call"""
        test_body = json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "messages": [{"role": "user", "content": "Test"}],
            "max_tokens": 5
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
        """Setup comprehensive data structures"""
        self.cocktails = {
            'martini': {
                'name': 'Martini',
                'ingredients': ['gin', 'dry vermouth', 'olive'],
                'glass': 'martini glass',
                'category': 'classic',
                'description': 'The epitome of cocktail sophistication',
                'strength': 'strong',
                'flavor_profile': ['dry', 'crisp', 'herbal'],
                'era': '1920s',
                'personality': 'sophisticated, sharp, elegant'
            },
            'old_fashioned': {
                'name': 'Old Fashioned',
                'ingredients': ['whiskey', 'sugar', 'bitters', 'orange'],
                'glass': 'rocks glass',
                'category': 'classic',
                'description': 'America\'s original cocktail',
                'strength': 'strong',
                'flavor_profile': ['sweet', 'bitter', 'woody'],
                'era': '1880s',
                'personality': 'traditional, bold, no-nonsense'
            },
            'negroni': {
                'name': 'Negroni',
                'ingredients': ['gin', 'campari', 'sweet vermouth'],
                'glass': 'rocks glass',
                'category': 'bitter',
                'description': 'Bold Italian aperitif with perfect balance',
                'strength': 'medium',
                'flavor_profile': ['bitter', 'herbal', 'complex'],
                'era': '1919',
                'personality': 'complex, mysterious, sophisticated'
            },
            'manhattan': {
                'name': 'Manhattan',
                'ingredients': ['whiskey', 'sweet vermouth', 'bitters'],
                'glass': 'coupe glass',
                'category': 'classic',
                'description': 'New York\'s sophisticated signature',
                'strength': 'strong',
                'flavor_profile': ['rich', 'smooth', 'warming'],
                'era': '1870s',
                'personality': 'urban, refined, timeless'
            },
            'margarita': {
                'name': 'Margarita',
                'ingredients': ['tequila', 'lime juice', 'triple sec'],
                'glass': 'margarita glass',
                'category': 'tropical',
                'description': 'Vibrant celebration in a glass',
                'strength': 'medium',
                'flavor_profile': ['citrus', 'refreshing', 'bright'],
                'era': '1940s',
                'personality': 'fun, energetic, festive'
            }
        }
        
        logger.info(f"✅ Loaded {len(self.cocktails)} premium cocktails")
    
    async def get_recommendation(self, movie_title: str) -> Dict[str, Any]:
        """Main recommendation method with comprehensive error handling"""
        self.api_calls_made += 1
        start_time = datetime.now()
        
        try:
            # Get movie context
            movie_context = self._get_movie_context(movie_title)
            
            # Try AI recommendation first
            if self.bedrock_client:
                try:
                    ai_result = await self._get_ai_recommendation(movie_context)
                    self.successful_calls += 1
                    processing_time = (datetime.now() - start_time).total_seconds()
                    
                    return {
                        **ai_result,
                        'processing_time_seconds': processing_time,
                        'api_call_number': self.api_calls_made,
                        'source': 'AI',
                        'model': self.model_id
                    }
                    
                except Exception as e:
                    logger.warning(f"AI recommendation failed: {e}, using fallback")
            
            # Use intelligent fallback
            fallback_result = self._get_intelligent_fallback(movie_context)
            processing_time = (datetime.now() - start_time).total_seconds()
            
            return {
                **fallback_result,
                'processing_time_seconds': processing_time,
                'api_call_number': self.api_calls_made,
                'source': 'Intelligent Fallback'
            }
            
        except Exception as e:
            logger.error(f"Complete recommendation failure: {e}")
            return {
                'success': False,
                'error': str(e),
                'movie_title': movie_title,
                'processing_time_seconds': (datetime.now() - start_time).total_seconds()
            }
    
    def _get_movie_context(self, movie_title: str) -> Dict[str, str]:
        """Get or create movie context"""
        # Known movies with rich context
        known_movies = {
            'casablanca': {
                'title': 'Casablanca',
                'year': '1942',
                'genre': 'Drama, Romance, War',
                'director': 'Michael Curtiz',
                'setting': 'WWII Morocco',
                'mood': 'romantic, nostalgic, sophisticated',
                'themes': 'sacrifice, love, duty',
                'visual_style': 'classic Hollywood, black and white',
                'cultural_significance': 'timeless classic'
            },
            'blade runner 2049': {
                'title': 'Blade Runner 2049',
                'year': '2017',
                'genre': 'Sci-Fi, Drama',
                'director': 'Denis Villeneuve',
                'setting': 'dystopian future Los Angeles',
                'mood': 'dark, contemplative, atmospheric',
                'themes': 'identity, humanity, memory',
                'visual_style': 'neo-noir, cyberpunk',
                'cultural_significance': 'modern sci-fi masterpiece'
            },
            'the godfather': {
                'title': 'The Godfather',
                'year': '1972',
                'genre': 'Crime, Drama',
                'director': 'Francis Ford Coppola',
                'setting': '1940s-50s New York',
                'mood': 'intense, dramatic, sophisticated',
                'themes': 'family, power, corruption',
                'visual_style': 'dark, intimate cinematography',
                'cultural_significance': 'cinema masterpiece'
            }
        }
        
        movie_key = movie_title.lower().strip()
        if movie_key in known_movies:
            return known_movies[movie_key]
        
        # Generate context for unknown movies
        return {
            'title': movie_title,
            'year': 'Unknown',
            'genre': 'Unknown',
            'director': 'Unknown',
            'setting': 'Various',
            'mood': 'Varied',
            'themes': 'Entertainment',
            'visual_style': 'Cinematic',
            'cultural_significance': 'Contemporary film'
        }
    
    async def _get_ai_recommendation(self, movie_context: Dict[str, str]) -> Dict[str, Any]:
        """Get AI recommendation with advanced prompt engineering"""
        
        # Create sophisticated prompt
        prompt = self._create_advanced_prompt(movie_context)
        
        # Make API call with retries
        ai_response = await self._call_claude_with_retries(prompt)
        
        # Parse response with multiple strategies
        parsed_result = self._parse_ai_response_advanced(ai_response)
        
        # Validate and enhance
        validated_result = self._validate_and_enhance_response(parsed_result, movie_context)
        
        return validated_result
    
    def _create_advanced_prompt(self, movie_context: Dict[str, str]) -> str:
        """Create advanced prompt with detailed context"""
        
        cocktail_profiles = []
        for name, details in self.cocktails.items():
            profile = f"""
🍸 {details['name']} ({details['era']})
   Personality: {details['personality']}
   Flavors: {', '.join(details['flavor_profile'])}
   Strength: {details['strength']}
   Context: {details['description']}"""
            cocktail_profiles.append(profile)
        
        prompt = f"""You are the world's most renowned cocktail sommelier and film expert, with decades of experience pairing drinks with cinematic experiences.

🎬 FILM ANALYSIS:
Title: {movie_context['title']}
Year: {movie_context['year']}
Genre: {movie_context['genre']}
Director: {movie_context['director']}
Setting: {movie_context['setting']}
Mood: {movie_context['mood']}
Themes: {movie_context['themes']}
Visual Style: {movie_context['visual_style']}
Cultural Impact: {movie_context['cultural_significance']}

🍸 AVAILABLE COCKTAIL COLLECTION:
{chr(10).join(cocktail_profiles)}

🎯 YOUR EXPERT MISSION:
Analyze every aspect of this film - its emotional journey, visual aesthetics, historical context, and thematic depth. Then select the ONE cocktail that creates the most harmonious and meaningful pairing experience.

Consider these sophisticated factors:
• Historical period alignment and cultural context
• Emotional resonance between drink and film atmosphere  
• Visual aesthetic harmony (colors, textures, presentation)
• Flavor complexity matching narrative sophistication
• Character psychology and social dynamics
• Optimal viewing experience enhancement

📋 RESPOND IN THIS EXACT JSON FORMAT:
{{
    "cocktail_name": "exact_name_from_collection",
    "confidence_score": 95,
    "primary_explanation": "Primary reason this pairing works (1-2 sentences)",
    "detailed_analysis": "Comprehensive analysis of the pairing (3-4 sentences)",
    "flavor_harmony": "How flavors complement the film experience",
    "cultural_connection": "Historical or cultural links between drink and film",
    "alternatives": ["second_choice", "third_choice"],
    "expert_notes": "Additional sommelier insights"
}}

CRITICAL: Use only cocktail names from the provided collection. Be confident and specific in your analysis."""

        return prompt
    
    async def _call_claude_with_retries(self, prompt: str, max_retries: int = 3) -> str:
        """Call Claude API with exponential backoff"""
        
        for attempt in range(max_retries):
            try:
                body = json.dumps({
                    "anthropic_version": "bedrock-2023-05-31",
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": 1500,
                    "temperature": 0.7,
                    "top_p": 0.9,
                    "top_k": 250
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
                    raise Exception("Invalid response structure")
                    
            except Exception as e:
                wait_time = (2 ** attempt) + 1  # Exponential backoff
                logger.warning(f"API attempt {attempt + 1} failed: {e}")
                
                if attempt == max_retries - 1:
                    raise e
                    
                await asyncio.sleep(wait_time)
        
        raise Exception("All API attempts exhausted")
    
    def _parse_ai_response_advanced(self, ai_text: str) -> Dict[str, Any]:
        """Advanced AI response parsing with multiple strategies"""
        
        # Strategy 1: Extract clean JSON
        json_result = self._extract_clean_json(ai_text)
        if json_result:
            return json_result
        
        # Strategy 2: Regex extraction with fallbacks
        return self._extract_with_regex_advanced(ai_text)
    
    def _extract_clean_json(self, text: str) -> Optional[Dict[str, Any]]:
        """Extract JSON with comprehensive cleaning"""
        
        # Clean text
        cleaned = text.strip()
        
        # Remove various markdown formats
        for marker in ['```json', '```JSON', '```', '`']:
            if cleaned.startswith(marker):
                cleaned = cleaned[len(marker):]
            if cleaned.endswith(marker):
                cleaned = cleaned[:-len(marker)]
        
        cleaned = cleaned.strip()
        
        # Try direct parsing
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            pass
        
        # Find JSON objects in text
        json_patterns = [
            r'\\{[^{}]*"cocktail_name"[^{}]*\\}',  # JSON with cocktail_name
            r'\\{.*?"cocktail_name".*?\\}',       # Any JSON with cocktail_name
            r'\\{[^{}]+\\}',                       # Simple JSON object
        ]
        
        for pattern in json_patterns:
            matches = re.findall(pattern, text, re.DOTALL | re.IGNORECASE)
            for match in matches:
                try:
                    return json.loads(match)
                except json.JSONDecodeError:
                    continue
        
        return None
    
    def _extract_with_regex_advanced(self, text: str) -> Dict[str, Any]:
        """Advanced regex extraction with intelligent parsing"""
        
        # Extract cocktail name
        cocktail_name = self._find_cocktail_in_text(text)
        
        # Extract confidence if present
        confidence_match = re.search(r'confidence["\']?\\s*:?\\s*([0-9]+)', text, re.IGNORECASE)
        confidence = int(confidence_match.group(1)) if confidence_match else 85
        
        # Extract explanations
        explanation_patterns = [
            r'explanation["\']?\\s*:?\\s*["\']([^"\']+)["\']',
            r'because\\s+([^.!?]+[.!?])',
            r'pairing\\s+works[^.!?]*([^.!?]+[.!?])'
        ]
        
        explanation = "Expert AI analysis selected this perfect pairing."
        for pattern in explanation_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                explanation = match.group(1).strip()
                break
        
        return {
            'cocktail_name': cocktail_name,
            'confidence_score': confidence,
            'primary_explanation': explanation,
            'detailed_analysis': text[:300] + "...",
            'flavor_harmony': 'Complementary flavor profiles',
            'cultural_connection': 'Thematic and aesthetic alignment',
            'alternatives': [name for name in self.cocktails.keys() if name != cocktail_name][:2],
            'expert_notes': 'Extracted from comprehensive AI analysis'
        }
    
    def _find_cocktail_in_text(self, text: str) -> str:
        """Find cocktail name in text with fuzzy matching"""
        text_lower = text.lower()
        
        # Direct name matching
        for cocktail_name, details in self.cocktails.items():
            if cocktail_name in text_lower or details['name'].lower() in text_lower:
                return cocktail_name
        
        # Partial matching
        for cocktail_name, details in self.cocktails.items():
            for word in cocktail_name.split('_'):
                if len(word) > 3 and word in text_lower:
                    return cocktail_name
        
        return 'martini'  # Sophisticated default
    
    def _validate_and_enhance_response(self, response: Dict[str, Any], movie_context: Dict[str, str]) -> Dict[str, Any]:
        """Validate and enhance the AI response"""
        
        # Ensure valid cocktail
        cocktail_name = response.get('cocktail_name', 'martini')
        if cocktail_name not in self.cocktails:
            cocktail_name = self._find_cocktail_in_text(str(response))
        
        cocktail_details = self.cocktails[cocktail_name]
        
        # Ensure valid alternatives
        alternatives = response.get('alternatives', [])
        valid_alternatives = []
        for alt in alternatives:
            if isinstance(alt, str):
                alt_clean = alt.lower().replace(' ', '_')
                if alt_clean in self.cocktails and alt_clean != cocktail_name:
                    valid_alternatives.append(alt_clean)
        
        # Fill alternatives if needed
        while len(valid_alternatives) < 2:
            for name in self.cocktails.keys():
                if name != cocktail_name and name not in valid_alternatives:
                    valid_alternatives.append(name)
                    break
            break
        
        return {
            'success': True,
            'movie': movie_context,
            'cocktail': cocktail_details,
            'recommendation': {
                'cocktail_name': cocktail_name,
                'confidence_score': response.get('confidence_score', 85),
                'primary_explanation': response.get('primary_explanation', 'Expert pairing selected by AI'),
                'detailed_analysis': response.get('detailed_analysis', 'Comprehensive analysis provided'),
                'flavor_harmony': response.get('flavor_harmony', 'Complementary profiles'),
                'cultural_connection': response.get('cultural_connection', 'Thematic alignment'),
                'alternatives': valid_alternatives,
                'expert_notes': response.get('expert_notes', 'Professional sommelier recommendation')
            }
        }
    
    def _get_intelligent_fallback(self, movie_context: Dict[str, str]) -> Dict[str, Any]:
        """Sophisticated rule-based fallback"""
        
        genre = movie_context.get('genre', '').lower()
        year = movie_context.get('year', '')
        mood = movie_context.get('mood', '').lower()
        setting = movie_context.get('setting', '').lower()
        
        # Advanced rule-based selection
        if 'romance' in genre or 'romantic' in mood:
            cocktail_name = 'manhattan'
            reasoning = "Romance films require cocktails with emotional depth and sophistication"
            
        elif 'crime' in genre or 'noir' in mood or 'dark' in mood:
            cocktail_name = 'negroni'
            reasoning = "Dark, complex films pair with bitter, sophisticated cocktails"
            
        elif 'action' in genre or 'thriller' in genre:
            cocktail_name = 'old_fashioned'
            reasoning = "High-energy films need bold, straightforward cocktails"
            
        elif 'comedy' in genre or 'fun' in mood:
            cocktail_name = 'margarita'
            reasoning = "Light-hearted entertainment pairs with refreshing, celebratory drinks"
            
        elif year and year.isdigit() and int(year) < 1970:
            cocktail_name = 'martini'
            reasoning = "Classic films deserve timeless, sophisticated cocktails"
            
        elif 'future' in setting or 'sci-fi' in genre:
            cocktail_name = 'martini'
            reasoning = "Futuristic themes pair with sleek, modernist cocktails"
            
        else:
            cocktail_name = 'manhattan'
            reasoning = "Sophisticated default for discerning film experiences"
        
        cocktail_details = self.cocktails[cocktail_name]
        alternatives = [name for name in self.cocktails.keys() if name != cocktail_name][:2]
        
        return {
            'success': True,
            'movie': movie_context,
            'cocktail': cocktail_details,
            'recommendation': {
                'cocktail_name': cocktail_name,
                'confidence_score': 80,
                'primary_explanation': reasoning,
                'detailed_analysis': f"Intelligent analysis based on {movie_context['title']}'s genre and characteristics",
                'flavor_harmony': f"{cocktail_details['personality']} matches film atmosphere",
                'cultural_connection': f"Era and style alignment with {movie_context['year']} cinema",
                'alternatives': alternatives,
                'expert_notes': 'Rule-based selection using film analysis'
            }
        }
    
    def get_system_stats(self) -> Dict[str, Any]:
        """Get system performance statistics"""
        uptime = (datetime.now() - self.start_time).total_seconds()
        success_rate = (self.successful_calls / max(self.api_calls_made, 1)) * 100
        
        return {
            'uptime_seconds': uptime,
            'total_api_calls': self.api_calls_made,
            'successful_api_calls': self.successful_calls,
            'success_rate_percent': round(success_rate, 2),
            'aws_connected': self.bedrock_client is not None,
            'model_id': getattr(self, 'model_id', 'N/A')
        }
    
    def sync_recommend(self, movie_title: str) -> Dict[str, Any]:
        """Synchronous wrapper for easy testing"""
        return asyncio.run(self.get_recommendation(movie_title))


async def run_comprehensive_test():
    """Comprehensive test of the production system"""
    print("🚀 Production LLM System - Comprehensive Test")
    print("=" * 70)
    
    agent = ProductionLLMAgent()
    
    test_cases = [
        "Casablanca",
        "Blade Runner 2049",
        "The Godfather",
        "Pulp Fiction",
        "Inception",
        "The Grand Budapest Hotel",
        "Mad Max: Fury Road"
    ]
    
    print(f"\\n🧪 Testing {len(test_cases)} movies...")
    
    for i, movie in enumerate(test_cases, 1):
        print(f"\\n[{i}/{len(test_cases)}] 🎬 {movie}")
        print("-" * 50)
        
        result = await agent.get_recommendation(movie)
        
        if result['success']:
            rec = result['recommendation']
            cocktail = result['cocktail']
            
            print(f"🍸 Perfect Match: {cocktail['name']}")
            print(f"🎯 Confidence: {rec['confidence_score']}/100")
            print(f"💭 Why: {rec['primary_explanation']}")
            print(f"🌟 Character: {cocktail['personality']}")
            print(f"🥃 Served: {cocktail['glass']}")
            print(f"⏱️  Response Time: {result['processing_time_seconds']:.2f}s")
            print(f"🤖 Source: {result['source']}")
            
            if 'model' in result:
                print(f"🧠 Model: {result['model'].split(':')[0]}")
            
        else:
            print(f"❌ Error: {result.get('error', 'Unknown error')}")
    
    # Show system statistics
    stats = agent.get_system_stats()
    print(f"\\n{'=' * 70}")
    print("📊 SYSTEM PERFORMANCE")
    print("=" * 70)
    print(f"⏱️  Uptime: {stats['uptime_seconds']:.1f} seconds")
    print(f"📞 API Calls: {stats['total_api_calls']}")
    print(f"✅ Success Rate: {stats['success_rate_percent']}%")
    print(f"🌐 AWS Status: {'Connected' if stats['aws_connected'] else 'Disconnected'}")
    print(f"🤖 Model: {stats['model_id']}")
    
    print(f"\\n🎉 Production Test Complete!")
    return agent

def interactive_production_test():
    """Interactive production testing"""
    print("🎬🍸 Production LLM System - Interactive Mode")
    print("=" * 50)
    print("Type movie titles to get expert recommendations")
    print("Type 'stats' to see system performance")
    print("Type 'quit' to exit")
    print("-" * 50)
    
    agent = ProductionLLMAgent()
    
    while True:
        user_input = input("\\nEnter movie title: ").strip()
        
        if user_input.lower() in ['quit', 'exit', 'q']:
            break
        elif user_input.lower() == 'stats':
            stats = agent.get_system_stats()
            print(f"\\n📊 System Stats:")
            print(f"   API Calls: {stats['total_api_calls']}")
            print(f"   Success Rate: {stats['success_rate_percent']}%")
            print(f"   AWS: {'✅' if stats['aws_connected'] else '❌'}")
            continue
        elif not user_input:
            continue
        
        print(f"\\n🤔 Analyzing '{user_input}' with AI...")
        result = agent.sync_recommend(user_input)
        
        if result['success']:
            rec = result['recommendation']
            cocktail = result['cocktail']
            
            print(f"\\n✨ Expert Recommendation:")
            print(f"🎬 Movie: {result['movie']['title']}")
            print(f"🍸 Perfect Cocktail: {cocktail['name']}")
            print(f"🎯 Confidence: {rec['confidence_score']}/100")
            print(f"💭 Primary Reason: {rec['primary_explanation']}")
            print(f"🔬 Detailed Analysis: {rec['detailed_analysis'][:150]}...")
            print(f"🌟 Cocktail Personality: {cocktail['personality']}")
            print(f"🔄 Alternatives: {', '.join(rec['alternatives'])}")
            print(f"⚡ Source: {result['source']}")
        else:
            print(f"❌ Error: {result.get('error', 'Unknown error')}")
    
    print("\\nThanks for testing the production system! 🚀")

if __name__ == "__main__":
    print("🚀 Production LLM System")
    print("Choose test mode:")
    print("1. Comprehensive automated test")
    print("2. Interactive testing")
    
    choice = input("Enter choice (1 or 2): ").strip()
    
    if choice == "2":
        interactive_production_test()
    else:
        asyncio.run(run_comprehensive_test())
