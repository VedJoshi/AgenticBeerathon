#!/usr/bin/env python3
"""
Clanker That Recommends Alcohol - Demo
Shows how to use the Clanker application
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

def main():
    # Sample movie data in the format provided by the frontend
    sample_movie_data = {
        "Title": "Casablanca",
        "Year": "1942",
        "Rated": "PG",
        "Released": "23 Jan 1943",
        "Runtime": "102 min",
        "Genre": "Drama, Romance, War",
        "Director": "Michael Curtiz",
        "Writer": "Philip G. Epstein, Julius J. Epstein, Howard Koch",
        "Actors": "Humphrey Bogart, Ingrid Bergman, Paul Henreid",
        "Plot": "A cynical expatriate American cafe owner struggles to decide whether or not to help his former lover and her fugitive husband escape the Nazis in French Morocco.",
        "Language": "English, French, German, Italian, Russian",
        "Country": "United States",
        "Awards": "Won 3 Oscars. 18 wins & 12 nominations total",
        "Poster": "https://m.media-amazon.com/images/M/MV5BNWEzN2U1YTYtYTQyMS00NTVkLWE2NGQtZWFlMmM0MDNjMmRiXkEyXkFqcGc@._V1_SX300.jpg",
        "Ratings": [
            {"Source": "Internet Movie Database", "Value": "8.5/10"},
            {"Source": "Rotten Tomatoes", "Value": "99%"},
            {"Source": "Metacritic", "Value": "100/100"}
        ],
        "Metascore": "100",
        "imdbRating": "8.5",
        "imdbVotes": "638,740",
        "imdbID": "tt0034583",
        "Type": "movie",
        "DVD": "N/A",
        "BoxOffice": "$4,219,709",
        "Production": "N/A",
        "Website": "N/A",
        "Response": "True"
    }
    
    print("🍸🎬 Clanker That Recommends Alcohol - Demo")
    print("=" * 60)
    
    # Initialize the app
    app = ClankerRecommender()
    
    # Process the movie data
    print("Processing movie data for Casablanca...")
    result = app.process_movie_data(sample_movie_data)
    
    # Display the result
    print("\nResult:")
    print(result)
    
    # Example of how to process JSON input directly
    print("\n\nExample of processing a JSON string input:")
    json_input = json.dumps(sample_movie_data)
    print(f"Input length: {len(json_input)} characters")
    print("Result would be the same as above")
    
    print("\n" + "=" * 60)
    print("🎉 Demo Complete!")

if __name__ == "__main__":
    main()
