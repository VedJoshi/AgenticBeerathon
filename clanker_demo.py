#!/usr/bin/env python3
"""
Clanker That Recommends Alcohol - Production Demo
Shows the complete JSON response structure that the frontend receives
"""

import sys
import os
import json
from dotenv import load_dotenv

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
from beer_clanker_bot.simplified_app import ClankerRecommender
from beer_clanker_bot.config import setup_logging

# Load environment variables and setup logging
load_dotenv()
setup_logging()

def print_section(title: str):
    """Print a formatted section header"""
    print(f"\n{'='*20} {title} {'='*20}")

def print_json_response(response, title: str):
    """Print formatted JSON response"""
    print_section(title)
    if hasattr(response, 'dict'):
        # Pydantic model
        response_dict = response.dict()
    else:
        # Regular dictionary
        response_dict = response
    
    print(json.dumps(response_dict, indent=2, ensure_ascii=False))

def main():
    """Demonstrate the production-ready Clanker application"""
    
    print("🍸🎬 CLANKER THAT RECOMMENDS ALCOHOL - PRODUCTION DEMO")
    print("=" * 70)
    print("This demo shows exactly what the frontend receives from the API")
    
    # Sample movie data that would come from the frontend (OMDB API format)
    sample_movies = [
        {
            "Title": "The Big Lebowski",
            "Year": "1998",
            "Rated": "R",
            "Runtime": "117 min",
            "Genre": "Comedy, Crime",
            "Director": "Joel Coen, Ethan Coen",
            "Plot": "Jeff 'The Dude' Lebowski, mistaken for a millionaire of the same name, seeks restitution for his ruined rug and enlists his bowling buddies to help get it.",
            "imdbRating": "8.1"
        },
        {
            "Title": "Casablanca",
            "Year": "1942",
            "Rated": "PG",
            "Runtime": "102 min",
            "Genre": "Drama, Romance, War",
            "Director": "Michael Curtiz",
            "Plot": "A cynical expatriate American cafe owner struggles to decide whether or not to help his former lover and her fugitive husband escape the Nazis in French Morocco.",
            "imdbRating": "8.5"
        }
    ]
    
    try:
        # Initialize the app
        print("\n🔧 Initializing Clanker That Recommends Alcohol...")
        app = ClankerRecommender()
        print("✅ Application initialized successfully!")
        
        # Process each movie
        for i, movie_data in enumerate(sample_movies, 1):
            print_section(f"MOVIE {i}: {movie_data['Title']}")
            
            # Show input data
            print("📥 INPUT (What frontend sends):")
            print(json.dumps({"movie_data": movie_data}, indent=2))
            
            # Process the movie data (this is what the API endpoint does)
            print(f"\n🤖 Processing recommendation for {movie_data['Title']}...")
            result = app.process_movie_data(movie_data)
            
            # Show the complete response structure
            print_json_response(result, "📤 COMPLETE API RESPONSE (What frontend receives)")
            
            # Break down the response structure for clarity
            if hasattr(result, 'success') and result.success:
                print_section("🎯 RESPONSE BREAKDOWN FOR FRONTEND")
                
                print("🎬 MOVIE INFO:")
                movie_info = result.movie.dict() if hasattr(result.movie, 'dict') else result.movie
                for key, value in movie_info.items():
                    print(f"  • {key}: {value}")
                
                print("\n🍸 DRINK RECOMMENDATION:")
                rec_info = result.recommendation.dict() if hasattr(result.recommendation, 'dict') else result.recommendation
                for key, value in rec_info.items():
                    if value:  # Only show non-empty values
                        print(f"  • {key}: {value}")
                
                print("\n📊 METADATA:")
                for key, value in result.metadata.items():
                    print(f"  • {key}: {value}")
                
                print("\n📄 FORMATTED TEXT (for display):")
                print("Available in result.formatted_text - ready for markdown rendering")
                
            else:
                print("❌ Error occurred - see error details in the response")
            
            if i < len(sample_movies):
                print("\n" + "─" * 70)
        
        # Show API endpoint examples
        print_section("🔗 API ENDPOINT USAGE EXAMPLES")
        
        print("""
Frontend can make requests to these endpoints:

1. POST /recommend-drink/
   Body: {"movie_data": {...OMDB_data...}}
   Returns: Complete ClankerResponse JSON

2. GET /health
   Returns: Service health status

3. GET /
   Returns: API information and available endpoints

Example cURL command:
curl -X POST "http://localhost:8000/recommend-drink/" \\
     -H "Content-Type: application/json" \\
     -d '{"movie_data": {"Title": "Casablanca", "Year": "1942", ...}}'
        """)
        
        print_section("✨ FRONTEND INTEGRATION NOTES")
        print("""
The frontend receives a structured JSON response with:

✅ SUCCESS RESPONSE:
  • success: true
  • movie: {title, year, genre, director, rating, runtime, plot}
  • recommendation: {name, type, base, key_flavors, glass, garnish, recipe, etc.}
  • formatted_text: Ready-to-display markdown text
  • metadata: Processing info, timestamps, API version

❌ ERROR RESPONSE:
  • success: false  
  • error: Human-readable error message
  • error_code: Programmatic error code
  • details: Additional error context

The frontend can:
1. Check response.success to determine if request succeeded
2. Use recommendation object for structured display
3. Use formatted_text for rich markdown display
4. Handle errors gracefully using error_code
        """)
        
    except Exception as e:
        print(f"\n❌ Demo failed with error: {str(e)}")
        print("Check your AWS credentials and configuration")
    
    print_section("🎉 DEMO COMPLETE")
    print("The production-ready Clanker API is ready for frontend integration!")

if __name__ == "__main__":
    main()
