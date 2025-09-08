#!/usr/bin/env python3
"""
Test script to demonstrate exactly what the frontend receives from the Clanker API
"""

import requests
import json
import time
import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def test_api_endpoint():
    """Test the API endpoint and show frontend interaction"""
    
    # Sample movie data that frontend would send
    movie_data = {
        "movie_data": {
            "Title": "Pulp Fiction",
            "Year": "1994",
            "Genre": "Crime, Drama",
            "Director": "Quentin Tarantino",
            "Plot": "The lives of two mob hitmen, a boxer, a gangster and his wife intertwine in four tales of violence and redemption.",
            "Runtime": "154 min",
            "imdbRating": "8.9"
        }
    }
    
    print("🍸🎬 CLANKER API TEST - FRONTEND INTERACTION DEMO")
    print("=" * 60)
    
    print("\n📤 FRONTEND SENDS (POST /recommend-drink/):")
    print(json.dumps(movie_data, indent=2))
    
    try:
        # Make request to API
        print("\n🔄 Making API request...")
        
        response = requests.post(
            "http://localhost:8000/recommend-drink/",
            json=movie_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"📊 HTTP Status: {response.status_code}")
        print(f"⏱️  Response Time: {response.elapsed.total_seconds():.2f}s")
        
        if response.status_code == 200:
            print("\n📥 FRONTEND RECEIVES (Complete JSON Response):")
            response_data = response.json()
            print(json.dumps(response_data, indent=2, ensure_ascii=False))
            
            print("\n🎯 FRONTEND CAN EXTRACT:")
            print(f"✅ Success: {response_data.get('success')}")
            print(f"🎬 Movie: {response_data.get('movie', {}).get('title')} ({response_data.get('movie', {}).get('year')})")
            print(f"🍸 Drink: {response_data.get('recommendation', {}).get('name')}")
            print(f"🥃 Type: {response_data.get('recommendation', {}).get('type')}")
            print(f"⏱️  Processing Time: {response_data.get('metadata', {}).get('processing_time_seconds')}s")
            
        else:
            print(f"\n❌ API Error ({response.status_code}):")
            print(response.text)
            
    except requests.exceptions.ConnectionError:
        print("\n❌ Cannot connect to API server at http://localhost:8000")
        print("💡 To test the API:")
        print("   1. Start the server: python src/beer_clanker_bot/api.py")
        print("   2. Run this test: python test_api.py")
        return False
        
    except Exception as e:
        print(f"\n❌ Error testing API: {str(e)}")
        return False
    
    return True

def test_health_endpoint():
    """Test the health endpoint"""
    print("\n" + "=" * 60)
    print("🩺 TESTING HEALTH ENDPOINT")
    
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        print(f"📊 HTTP Status: {response.status_code}")
        
        if response.status_code == 200:
            health_data = response.json()
            print("📥 Health Response:")
            print(json.dumps(health_data, indent=2))
        else:
            print(f"❌ Health check failed: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Health endpoint not accessible")
    except Exception as e:
        print(f"❌ Error checking health: {str(e)}")

if __name__ == "__main__":
    # Test if we can import the application directly
    print("🧪 ALTERNATIVE: DIRECT APPLICATION TESTING")
    print("=" * 60)
    
    try:
        from beer_clanker_bot.simplified_app import ClankerRecommender
        from beer_clanker_bot.config import setup_logging
        
        setup_logging()
        
        # Test direct application usage (bypassing API)
        app = ClankerRecommender()
        
        movie_data = {
            "Title": "Pulp Fiction",
            "Year": "1994", 
            "Genre": "Crime, Drama",
            "Director": "Quentin Tarantino",
            "Plot": "The lives of two mob hitmen, a boxer, a gangster and his wife intertwine in four tales of violence and redemption.",
            "Runtime": "154 min",
            "imdbRating": "8.9"
        }
        
        print("\n📤 INPUT:")
        print(json.dumps(movie_data, indent=2))
        
        print("\n🤖 Processing with Clanker...")
        result = app.process_movie_data(movie_data)
        
        print(f"\n📥 DIRECT OUTPUT (what API would return):")
        if hasattr(result, 'model_dump'):
            response_dict = result.model_dump()
        elif hasattr(result, 'dict'):
            response_dict = result.dict()
        else:
            response_dict = result
            
        print(json.dumps(response_dict, indent=2, ensure_ascii=False))
        
        print("\n✅ Direct application test successful!")
        print("\n💡 For full API testing, start the server with:")
        print("   python src/beer_clanker_bot/api.py")
        
    except Exception as e:
        print(f"❌ Direct test failed: {str(e)}")
    
    # Try API endpoints if server is running
    if test_api_endpoint():
        test_health_endpoint()
        
    print("\n🎉 Testing complete!")
