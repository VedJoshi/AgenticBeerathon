"""
Movie Tool for Clanker
Handles movie data retrieval from OMDB API
"""
import os
import requests
import asyncio
import aiohttp
from typing import Dict, Optional, List
from dotenv import load_dotenv

# Try multiple possible locations for .env file
def load_env_file():
    possible_paths = [
        '.env',  # Current directory
        '../.env',  # Parent directory
        '../../.env',  # Grandparent directory
        os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), '.env'),  # From tools dir
        r'C:\Users\vedti\Downloads\BoNUS\.env'  # Absolute path as fallback
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            load_dotenv(path)
            print(f"Loaded .env from: {path}")
            break

load_env_file()

class MovieTool:
    """Tool for fetching movie data from OMDB API"""
    
    def __init__(self):
        self.api_key = os.getenv('OMDB_API_KEY')
        self.base_url = "http://www.omdbapi.com/"
        
        if not self.api_key:
            raise ValueError("OMDB_API_KEY not found in environment variables")
    
    async def search_movie(self, title: str) -> Optional[Dict]:
        """
        Search for a movie by title
        
        Args:
            title (str): Movie title to search for
            
        Returns:
            Dict: Movie data or None if not found
        """
        try:
            async with aiohttp.ClientSession() as session:
                params = {
                    'apikey': self.api_key,
                    't': title,  # Search by title
                    'type': 'movie',
                    'plot': 'full'
                }
                
                async with session.get(self.base_url, params=params) as response:
                    data = await response.json()
                    
                    if data.get('Response') == 'True':
                        return self._format_movie_data(data)
                    else:
                        print(f"Movie not found: {data.get('Error', 'Unknown error')}")
                        return None
                        
        except Exception as e:
            print(f"Error searching for movie '{title}': {str(e)}")
            return None
    
    async def get_movie_details(self, imdb_id: str) -> Optional[Dict]:
        """
        Get detailed movie information by IMDb ID
        
        Args:
            imdb_id (str): IMDb ID (e.g., 'tt0111161')
            
        Returns:
            Dict: Detailed movie data or None if not found
        """
        try:
            async with aiohttp.ClientSession() as session:
                params = {
                    'apikey': self.api_key,
                    'i': imdb_id,  # Search by IMDb ID
                    'plot': 'full'
                }
                
                async with session.get(self.base_url, params=params) as response:
                    data = await response.json()
                    
                    if data.get('Response') == 'True':
                        return self._format_movie_data(data)
                    else:
                        print(f"Movie not found: {data.get('Error', 'Unknown error')}")
                        return None
                        
        except Exception as e:
            print(f"Error getting movie details for '{imdb_id}': {str(e)}")
            return None
    
    def _format_movie_data(self, raw_data: Dict) -> Dict:
        """
        Format raw OMDB data into clean structure
        
        Args:
            raw_data (Dict): Raw data from OMDB API
            
        Returns:
            Dict: Formatted movie data
        """
        return {
            'title': raw_data.get('Title', ''),
            'year': raw_data.get('Year', ''),
            'genre': raw_data.get('Genre', ''),
            'director': raw_data.get('Director', ''),
            'plot': raw_data.get('Plot', ''),
            'imdb_rating': raw_data.get('imdbRating', ''),
            'imdb_id': raw_data.get('imdbID', ''),
            'runtime': raw_data.get('Runtime', ''),
            'actors': raw_data.get('Actors', ''),
            'country': raw_data.get('Country', ''),
            'language': raw_data.get('Language', ''),
            'poster': raw_data.get('Poster', ''),
            'awards': raw_data.get('Awards', ''),
            'box_office': raw_data.get('BoxOffice', ''),
            'production': raw_data.get('Production', ''),
            'rated': raw_data.get('Rated', '')
        }
    
    async def search_multiple_movies(self, titles: List[str]) -> List[Dict]:
        """
        Search for multiple movies concurrently
        
        Args:
            titles (List[str]): List of movie titles
            
        Returns:
            List[Dict]: List of movie data (None entries for movies not found)
        """
        tasks = [self.search_movie(title) for title in titles]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out exceptions and None results
        return [result for result in results if isinstance(result, dict)]
    
    def sync_search_movie(self, title: str) -> Optional[Dict]:
        """
        Synchronous version of search_movie for easier testing
        
        Args:
            title (str): Movie title to search for
            
        Returns:
            Dict: Movie data or None if not found
        """
        try:
            params = {
                'apikey': self.api_key,
                't': title,
                'type': 'movie',
                'plot': 'full'
            }
            
            response = requests.get(self.base_url, params=params)
            data = response.json()
            
            if data.get('Response') == 'True':
                return self._format_movie_data(data)
            else:
                print(f"Movie not found: {data.get('Error', 'Unknown error')}")
                return None
                
        except Exception as e:
            print(f"Error searching for movie '{title}': {str(e)}")
            return None

# Convenience function for quick testing
def quick_movie_search(title: str) -> Optional[Dict]:
    """Quick synchronous movie search for testing"""
    tool = MovieTool()
    return tool.sync_search_movie(title)

# Test the tool if run directly
if __name__ == "__main__":
    # Test with a popular movie
    test_title = "The Grand Budapest Hotel"
    print(f"Testing movie search for: {test_title}")
    
    tool = MovieTool()
    result = tool.sync_search_movie(test_title)
    
    if result:
        print(f"✅ Found: {result['title']} ({result['year']})")
        print(f"Genre: {result['genre']}")
        print(f"Director: {result['director']}")
        print(f"IMDb Rating: {result['imdb_rating']}")
        print(f"Plot: {result['plot'][:100]}...")
    else:
        print("❌ Movie not found")
