#!/usr/bin/env python3
"""
VinoFlix Demo Script
Demonstrates the core functionality without the UI
"""

import sys
import os
from dotenv import load_dotenv

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
from beer_clanker_bot.main_app import VinoFlix

# Load environment variables
load_dotenv()

def demo_movie_to_cocktail():
    """Demonstrate movie → cocktail recommendation"""
    print("🎬 DEMO: Movie → Cocktail Recommendation")
    print("-" * 50)
    
    app = VinoFlix(
        s3_bucket=os.getenv('S3_BUCKET_NAME'),
        s3_csv_key=os.getenv('S3_CSV_KEY')
    )
    
    movies = ["Casablanca", "The Godfather", "Blade Runner 2049"]
    
    for movie in movies:
        print(f"\n🎬 Testing: {movie}")
        result = app.movie_to_cocktail(movie)
        print(result)
        print("\n" + "="*60)

def demo_cocktail_to_movie():
    """Demonstrate cocktail → movie recommendation"""
    print("\n🍸 DEMO: Cocktail → Movie Recommendation")
    print("-" * 50)
    
    app = VinoFlix(
        s3_bucket=os.getenv('S3_BUCKET_NAME'),
        s3_csv_key=os.getenv('S3_CSV_KEY')
    )
    
    # Get available cocktails
    cocktails = app.get_cocktail_suggestions()
    test_cocktails = cocktails[:3] if len(cocktails) >= 3 else cocktails
    
    for cocktail_name in test_cocktails:
        print(f"\n🍸 Testing: {cocktail_name}")
        result = app.get_recommendation(cocktail_name)
        print(result)
        print("\n" + "="*60)

def show_available_cocktails():
    """Show all available cocktails in the collection"""
    print("\n🍸 Available Cocktails in Your Collection")
    print("-" * 50)
    
    app = VinoFlix(
        s3_bucket=os.getenv('S3_BUCKET_NAME'),
        s3_csv_key=os.getenv('S3_CSV_KEY')
    )
    
    cocktails = app.get_cocktail_suggestions()
    
    for i, cocktail in enumerate(cocktails, 1):
        print(f"{i:2d}. {cocktail}")
    
    print(f"\nTotal: {len(cocktails)} cocktails loaded from S3")

if __name__ == "__main__":
    print("🍸🎬 VinoFlix Demo")
    print("=" * 60)
    print("Testing AI-powered movie and cocktail pairings...")
    
    try:
        # Show available data
        show_available_cocktails()
        
        # Demo movie → cocktail (just one example to keep it quick)
        print("\n🎬 Quick Movie → Cocktail Demo")
        print("-" * 40)
        
        app = VinoFlix(
            s3_bucket=os.getenv('S3_BUCKET_NAME'),
            s3_csv_key=os.getenv('S3_CSV_KEY')
        )
        
        print("\n🎬 Testing: Jurassic Park")
        result = app.movie_to_cocktail("Jurassic Park")
        print(result)
        
        print("\n🍸 Testing: Martini")
        result = app.get_recommendation("Martini")
        print(result)
        
        print("\n" + "=" * 60)
        print("🎉 Demo Complete!")
        print("\n💡 To run the full interactive app:")
        print("   streamlit run src/beer_clanker_bot/streamlit_app.py")
        print("\n🌐 Then open: http://localhost:8501")
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        print("\n🔧 Try running: python test_vinoflix.py")
