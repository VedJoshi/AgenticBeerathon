#!/usr/bin/env python3
"""
Example of using the ClankerRecommender class directly
"""

import sys
import os
import json
from dotenv import load_dotenv

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
from beer_clanker_bot.simplified_app import ClankerRecommender

# Load environment variables
load_dotenv()

# Initialize the app
app = ClankerRecommender()

# You can pass a Python dictionary directly
movie_data = {
    "Title": "The Godfather",
    "Year": "1972",
    "Genre": "Crime, Drama",
    "Director": "Francis Ford Coppola",
    "Plot": "The aging patriarch of an organized crime dynasty transfers control of his clandestine empire to his reluctant son.",
    "Runtime": "175 min",
    "imdbRating": "9.2"
}

print("🍸🎬 Clanker That Recommends Alcohol")
print("=" * 60)
print("Processing movie data for The Godfather...")
result = app.process_movie_data(movie_data)
print("\nResult:")
print(result)

# Or you can pass a JSON string
print("\n\nProcessing a JSON string input:")
json_input = json.dumps(movie_data)
result = app.process_movie_data(json_input)
print("\nResult:")
print(result)
