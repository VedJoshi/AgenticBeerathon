import requests
from typing import Optional, Dict

class OMDBClient:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "http://www.omdbapi.com/"
    
    def get_movie(self, title: str) -> Optional[Dict]:
        """Get movie details from OMDB API"""
        params = {
            'apikey': self.api_key,
            't': title,
            'plot': 'full'
        }
        
        try:
            response = requests.get(self.base_url, params=params)
            if response.status_code == 200:
                data = response.json()
                if data.get('Response') == 'True':
                    return {
                        'title': data.get('Title', ''),
                        'year': data.get('Year', ''),
                        'genre': data.get('Genre', ''),
                        'plot': data.get('Plot', ''),
                        'director': data.get('Director', ''),
                        'imdb_rating': data.get('imdbRating', 'N/A'),
                        'runtime': data.get('Runtime', ''),
                        'actors': data.get('Actors', ''),
                        'country': data.get('Country', ''),
                        'language': data.get('Language', '')
                    }
        except Exception as e:
            print(f"Error fetching movie data: {e}")
        
        return None
