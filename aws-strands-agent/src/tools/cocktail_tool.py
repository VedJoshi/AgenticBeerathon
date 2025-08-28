"""
Cocktail Tool for Clanker
Handles cocktail data retrieval from local cocktail database
"""
import json
import os
import asyncio
from typing import Dict, Optional, List
import random
import glob

class CocktailTool:
    """Tool for fetching cocktail data from local cocktail database"""
    
    def __init__(self):
        self.cocktails_path = r"C:\Users\vedti\Downloads\BoNUS\data\cocktails\data\cocktails"
        self._cocktail_cache = {}
        self._load_cocktails()
    
    def _load_cocktails(self):
        """Load all cocktails from local database into cache"""
        try:
            cocktail_dirs = [d for d in os.listdir(self.cocktails_path) 
                           if os.path.isdir(os.path.join(self.cocktails_path, d))]
            
            print(f"Loading {len(cocktail_dirs)} cocktails from local database...")
            
            for cocktail_dir in cocktail_dirs:
                data_file = os.path.join(self.cocktails_path, cocktail_dir, 'data.json')
                if os.path.exists(data_file):
                    try:
                        with open(data_file, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                            formatted_data = self._format_cocktail_data(data)
                            self._cocktail_cache[cocktail_dir] = formatted_data
                            # Also cache by name for easy lookup
                            name_key = data.get('name', '').lower().replace(' ', '_').replace('-', '_')
                            if name_key:
                                self._cocktail_cache[name_key] = formatted_data
                    except Exception as e:
                        print(f"Error loading {cocktail_dir}: {str(e)}")
            
            print(f"✅ Loaded {len([k for k in self._cocktail_cache.keys() if not '_' in k or k.count('_') < 2])} cocktails successfully")
            
        except Exception as e:
            print(f"Error loading cocktails: {str(e)}")
    
    async def search_cocktail(self, name: str) -> Optional[Dict]:
        """
        Search for a cocktail by name
        
        Args:
            name (str): Cocktail name to search for
            
        Returns:
            Dict: Cocktail data or None if not found
        """
        name_key = name.lower().replace(' ', '_').replace('-', '_')
        
        # Direct match
        if name_key in self._cocktail_cache:
            return self._cocktail_cache[name_key]
        
        # Fuzzy search
        for key, cocktail in self._cocktail_cache.items():
            if isinstance(cocktail, dict) and 'name' in cocktail:
                if name.lower() in cocktail['name'].lower():
                    return cocktail
        
        print(f"Cocktail not found: {name}")
        return None
    
    async def get_random_cocktail(self) -> Optional[Dict]:
        """
        Get a random cocktail
        
        Returns:
            Dict: Random cocktail data or None if error
        """
        try:
            # Get only cocktail directories (not name keys)
            cocktail_keys = [k for k in self._cocktail_cache.keys() if '-' in k or '_' in k]
            if cocktail_keys:
                random_key = random.choice(cocktail_keys)
                return self._cocktail_cache[random_key]
            return None
        except Exception as e:
            print(f"Error getting random cocktail: {str(e)}")
            return None
    
    async def search_by_ingredient(self, ingredient: str) -> List[Dict]:
        """
        Search for cocktails by main ingredient
        
        Args:
            ingredient (str): Main ingredient (e.g., 'gin', 'vodka', 'whiskey')
            
        Returns:
            List[Dict]: List of cocktails containing the ingredient
        """
        try:
            matching_cocktails = []
            ingredient_lower = ingredient.lower()
            
            for key, cocktail in self._cocktail_cache.items():
                if isinstance(cocktail, dict) and 'ingredients' in cocktail:
                    for ing in cocktail['ingredients']:
                        if ingredient_lower in ing.lower():
                            matching_cocktails.append(cocktail)
                            break
                    
                    if len(matching_cocktails) >= 10:  # Limit results
                        break
            
            return matching_cocktails
            
        except Exception as e:
            print(f"Error searching by ingredient '{ingredient}': {str(e)}")
            return []
    
    async def get_cocktails_by_tag(self, tag: str) -> List[Dict]:
        """
        Get cocktails by tag (e.g., 'Contemporary Classics', 'IBA Cocktail')
        
        Args:
            tag (str): Tag to search for
            
        Returns:
            List[Dict]: List of cocktails with the tag
        """
        try:
            matching_cocktails = []
            tag_lower = tag.lower()
            
            for key, cocktail in self._cocktail_cache.items():
                if isinstance(cocktail, dict) and 'tags' in cocktail:
                    for cocktail_tag in cocktail['tags']:
                        if tag_lower in cocktail_tag.lower():
                            matching_cocktails.append(cocktail)
                            break
                    
                    if len(matching_cocktails) >= 10:  # Limit results
                        break
            
            return matching_cocktails
            
        except Exception as e:
            print(f"Error searching by tag '{tag}': {str(e)}")
            return []
    
    async def get_cocktails_by_spirit(self, spirit: str) -> List[Dict]:
        """
        Get cocktails by primary spirit
        
        Args:
            spirit (str): Primary spirit (gin, vodka, whiskey, rum, etc.)
            
        Returns:
            List[Dict]: List of cocktails with that primary spirit
        """
        return await self.search_by_ingredient(spirit)
    
    def _format_cocktail_data(self, raw_data: Dict) -> Dict:
        """
        Format raw local data into clean structure
        
        Args:
            raw_data (Dict): Raw data from local JSON
            
        Returns:
            Dict: Formatted cocktail data
        """
        # Extract ingredients with amounts
        ingredients = []
        for ingredient in raw_data.get('ingredients', []):
            name = ingredient.get('name', '')
            amount = ingredient.get('amount', '')
            units = ingredient.get('units', '')
            
            if name:
                if amount and units:
                    ingredients.append(f"{amount}{units} {name}")
                else:
                    ingredients.append(name)
        
        return {
            'name': raw_data.get('name', ''),
            'id': raw_data.get('_id', ''),
            'description': raw_data.get('description', ''),
            'instructions': raw_data.get('instructions', ''),
            'glass': raw_data.get('glass', ''),
            'method': raw_data.get('method', ''),
            'garnish': raw_data.get('garnish', ''),
            'abv': raw_data.get('abv', 0),
            'tags': raw_data.get('tags', []),
            'ingredients': ingredients,
            'source': raw_data.get('source', ''),
            'images': raw_data.get('images', [])
        }
    
    def sync_search_cocktail(self, name: str) -> Optional[Dict]:
        """
        Synchronous version of search_cocktail for easier testing
        
        Args:
            name (str): Cocktail name to search for
            
        Returns:
            Dict: Cocktail data or None if not found
        """
        name_key = name.lower().replace(' ', '_').replace('-', '_')
        
        # Direct match
        if name_key in self._cocktail_cache:
            return self._cocktail_cache[name_key]
        
        # Fuzzy search
        for key, cocktail in self._cocktail_cache.items():
            if isinstance(cocktail, dict) and 'name' in cocktail:
                if name.lower() in cocktail['name'].lower():
                    return cocktail
        
        print(f"Cocktail not found: {name}")
        return None
    
    def sync_get_random_cocktail(self) -> Optional[Dict]:
        """
        Synchronous version of get_random_cocktail for testing
        
        Returns:
            Dict: Random cocktail data or None if error
        """
        try:
            # Get only cocktail directories (not name keys)
            cocktail_keys = [k for k in self._cocktail_cache.keys() if '-' in k]
            if cocktail_keys:
                random_key = random.choice(cocktail_keys)
                return self._cocktail_cache[random_key]
            return None
        except Exception as e:
            print(f"Error getting random cocktail: {str(e)}")
            return None
    
    def get_all_cocktail_names(self) -> List[str]:
        """Get list of all available cocktail names"""
        names = []
        for key, cocktail in self._cocktail_cache.items():
            if isinstance(cocktail, dict) and 'name' in cocktail and '-' in key:
                names.append(cocktail['name'])
        return sorted(names)
    
    def get_cocktails_by_mood(self, mood: str) -> List[Dict]:
        """
        Get cocktails that match a mood based on their characteristics
        
        Args:
            mood (str): Mood like 'elegant', 'strong', 'refreshing', 'tropical'
            
        Returns:
            List[Dict]: List of matching cocktails
        """
        mood_mappings = {
            'elegant': ['champagne', 'french', 'sophisticated', 'elegant'],
            'strong': ['whiskey', 'bourbon', 'neat', 'old fashioned', 'strong', 'manhattan', 'sazerac'],
            'refreshing': ['gin', 'citrus', 'mint', 'lime', 'fresh', 'light'],
            'tropical': ['rum', 'coconut', 'pineapple', 'tiki', 'tropical'],
            'classic': ['martini', 'manhattan', 'negroni', 'classic', 'traditional'],
            'modern': ['contemporary', 'new', 'modern'],
            'sophisticated': ['complex', 'bitter', 'aperitif', 'sophisticated', 'negroni']
        }
        
        mood_keywords = mood_mappings.get(mood.lower(), [mood.lower()])
        matching_cocktails = []
        
        for key, cocktail in self._cocktail_cache.items():
            if isinstance(cocktail, dict) and '-' in key:
                # Check name, description, and tags
                text_to_search = ""
                if cocktail.get('name'):
                    text_to_search += cocktail['name'].lower() + ' '
                if cocktail.get('description'):
                    text_to_search += cocktail['description'].lower() + ' '
                if cocktail.get('tags'):
                    text_to_search += ' '.join(str(tag).lower() for tag in cocktail['tags']) + ' '
                if cocktail.get('ingredients'):
                    text_to_search += ' '.join(str(ing).lower() for ing in cocktail['ingredients']) + ' '
                
                for keyword in mood_keywords:
                    if keyword in text_to_search:
                        matching_cocktails.append(cocktail)
                        break
                
                if len(matching_cocktails) >= 8:
                    break
        
        return matching_cocktails

# Convenience function for quick testing
def quick_cocktail_search(name: str) -> Optional[Dict]:
    """Quick synchronous cocktail search for testing"""
    tool = CocktailTool()
    return tool.sync_search_cocktail(name)

# Test the tool if run directly
if __name__ == "__main__":
    print("Testing Local Cocktail Tool...")
    
    tool = CocktailTool()
    
    # Test specific cocktail search
    print("\n1. Testing search for 'French 75':")
    result = tool.sync_search_cocktail("French 75")
    if result:
        print(f"✅ Found: {result['name']}")
        print(f"Description: {result['description'][:100]}...")
        print(f"Glass: {result['glass']}")
        print(f"Ingredients: {', '.join(result['ingredients'][:3])}...")
        print(f"Instructions: {result['instructions'][:100]}...")
    else:
        print("❌ Cocktail not found")
    
    # Test random cocktail
    print("\n2. Testing random cocktail:")
    random_result = tool.sync_get_random_cocktail()
    if random_result:
        print(f"✅ Random cocktail: {random_result['name']}")
        print(f"Tags: {', '.join(random_result.get('tags', []))}")
    else:
        print("❌ Random cocktail failed")
    
    # Test cocktail count
    print(f"\n3. Total cocktails available: {len(tool.get_all_cocktail_names())}")
    print("Sample cocktails:", tool.get_all_cocktail_names()[:5])
