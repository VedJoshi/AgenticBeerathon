#!/usr/bin/env python3
"""
Command-line interface for cocktail vector search
"""

import argparse
import os
import sys
import json
from typing import List, Dict

# Add the project root to the path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

def setup_database_demo():
    """Setup demo database connection"""
    db_config = {
        'host': os.getenv('DB_HOST', 'localhost'),
        'database': os.getenv('DB_NAME', 'agenticbeerathon'),
        'user': os.getenv('DB_USER', 'postgres'),
        'password': os.getenv('DB_PASSWORD', ''),
        'port': int(os.getenv('DB_PORT', '5432'))
    }
    return db_config

def search_similar_cocktails(cocktail_name: str, max_results: int = 5):
    """Search for cocktails similar to the given cocktail"""
    try:
        from src.utils.vector_search_api import create_search_api
        
        db_config = setup_database_demo()
        search_api = create_search_api(db_config)
        
        results = search_api.find_similar_cocktails_by_flavor(
            cocktail_name, 
            max_results=max_results,
            similarity_threshold=0.6
        )
        
        if not results:
            print(f"No similar cocktails found for '{cocktail_name}'")
            return
        
        print(f"\n🍸 Cocktails similar to '{cocktail_name}':")
        print("=" * 50)
        
        for i, match in enumerate(results, 1):
            print(f"{i}. {match.cocktail_name}")
            print(f"   Similarity: {match.similarity_score:.2%}")
            print(f"   Method: {match.method or 'N/A'}")
            print(f"   Glass: {match.glass or 'N/A'}")
            if match.abv:
                print(f"   ABV: {match.abv}%")
            if match.description:
                desc = match.description[:100] + "..." if len(match.description) > 100 else match.description
                print(f"   Description: {desc}")
            print()
            
    except Exception as e:
        print(f"Error searching for similar cocktails: {e}")

def search_by_flavor(flavor_description: str, max_results: int = 5):
    """Search cocktails by flavor description"""
    try:
        from src.utils.vector_search_api import create_search_api
        
        db_config = setup_database_demo()
        search_api = create_search_api(db_config)
        
        results = search_api.search_cocktails_by_flavor_description(
            flavor_description,
            max_results=max_results,
            similarity_threshold=0.4
        )
        
        if not results:
            print(f"No cocktails found matching flavor: '{flavor_description}'")
            return
        
        print(f"\n🍹 Cocktails matching flavor '{flavor_description}':")
        print("=" * 50)
        
        for i, match in enumerate(results, 1):
            print(f"{i}. {match.cocktail_name}")
            print(f"   Similarity: {match.similarity_score:.2%}")
            print(f"   Method: {match.method or 'N/A'}")
            if match.tags:
                print(f"   Tags: {', '.join(match.tags)}")
            if match.description:
                desc = match.description[:100] + "..." if len(match.description) > 100 else match.description
                print(f"   Description: {desc}")
            print()
            
    except Exception as e:
        print(f"Error searching by flavor: {e}")

def search_by_ingredients(ingredients: List[str], max_results: int = 5):
    """Search cocktails by ingredients"""
    try:
        from src.utils.vector_search_api import create_search_api
        
        db_config = setup_database_demo()
        search_api = create_search_api(db_config)
        
        results = search_api.find_cocktails_by_ingredient_similarity(
            ingredients,
            similarity_threshold=0.3,
            max_results=max_results
        )
        
        if not results:
            print(f"No cocktails found with ingredients: {', '.join(ingredients)}")
            return
        
        print(f"\n🥃 Cocktails with ingredients: {', '.join(ingredients)}")
        print("=" * 50)
        
        for i, match in enumerate(results, 1):
            print(f"{i}. {match['cocktail_name']}")
            print(f"   Match: {match['matching_ingredients']}/{match['total_ingredients']} ingredients ({match['match_percentage']:.1%})")
            if match['description']:
                desc = match['description'][:100] + "..." if len(match['description']) > 100 else match['description']
                print(f"   Description: {desc}")
            print()
            
    except Exception as e:
        print(f"Error searching by ingredients: {e}")

def get_ingredient_recommendations(cocktail_name: str, max_results: int = 5):
    """Get ingredient recommendations for a cocktail"""
    try:
        from src.utils.vector_search_api import create_search_api
        
        db_config = setup_database_demo()
        search_api = create_search_api(db_config)
        
        results = search_api.get_ingredient_recommendations(
            cocktail_name,
            max_results=max_results
        )
        
        if not results:
            print(f"No ingredient recommendations found for '{cocktail_name}'")
            return
        
        print(f"\n🧊 Ingredient recommendations for '{cocktail_name}':")
        print("=" * 50)
        
        for i, match in enumerate(results, 1):
            print(f"{i}. {match.ingredient_name}")
            print(f"   Similarity: {match.similarity_score:.2%}")
            print(f"   Category: {match.category}")
            if match.strength:
                print(f"   Strength: {match.strength}%")
            if match.description:
                desc = match.description[:100] + "..." if len(match.description) > 100 else match.description
                print(f"   Description: {desc}")
            print()
            
    except Exception as e:
        print(f"Error getting ingredient recommendations: {e}")

def show_cocktail_details(cocktail_name: str):
    """Show detailed information about a cocktail"""
    try:
        from src.utils.vector_search_api import create_search_api
        
        db_config = setup_database_demo()
        search_api = create_search_api(db_config)
        
        # First find the cocktail
        import psycopg2
        conn = psycopg2.connect(**db_config)
        cur = conn.cursor()
        
        cur.execute("SELECT id FROM cocktails WHERE name ILIKE %s LIMIT 1", (f"%{cocktail_name}%",))
        result = cur.fetchone()
        
        if not result:
            print(f"Cocktail '{cocktail_name}' not found")
            cur.close()
            conn.close()
            return
        
        cocktail_id = result[0]
        cur.close()
        conn.close()
        
        details = search_api.get_cocktail_details(cocktail_id)
        
        if not details:
            print(f"No details found for '{cocktail_name}'")
            return
        
        print(f"\n🍸 {details['name']}")
        print("=" * 50)
        
        if details['description']:
            print(f"Description: {details['description']}")
            print()
        
        if details['instructions']:
            print(f"Instructions: {details['instructions']}")
            print()
        
        print(f"Method: {details['method'] or 'N/A'}")
        print(f"Glass: {details['glass'] or 'N/A'}")
        
        if details['abv']:
            print(f"ABV: {details['abv']}%")
        
        if details['garnish']:
            print(f"Garnish: {details['garnish']}")
        
        if details['tags']:
            print(f"Tags: {', '.join(details['tags'])}")
        
        if details['ingredients']:
            print("\nIngredients:")
            for ing in details['ingredients']:
                if ing and isinstance(ing, dict):
                    amount_str = f"{ing.get('amount', '')} {ing.get('units', '')}" if ing.get('amount') else ""
                    optional_str = " (optional)" if ing.get('optional') else ""
                    print(f"  • {amount_str} {ing.get('name', '')}{optional_str}")
                    if ing.get('note'):
                        print(f"    Note: {ing['note']}")
        
        print()
            
    except Exception as e:
        print(f"Error showing cocktail details: {e}")

def main():
    parser = argparse.ArgumentParser(description="Cocktail Vector Search CLI")
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Similar cocktails command
    similar_parser = subparsers.add_parser('similar', help='Find similar cocktails')
    similar_parser.add_argument('cocktail', help='Name of the cocktail to find similar ones')
    similar_parser.add_argument('--max-results', type=int, default=5, help='Maximum number of results')
    
    # Flavor search command
    flavor_parser = subparsers.add_parser('flavor', help='Search by flavor description')
    flavor_parser.add_argument('description', help='Flavor description (e.g., "citrusy and refreshing")')
    flavor_parser.add_argument('--max-results', type=int, default=5, help='Maximum number of results')
    
    # Ingredient search command
    ingredient_parser = subparsers.add_parser('ingredients', help='Search by ingredients')
    ingredient_parser.add_argument('ingredients', nargs='+', help='List of ingredients')
    ingredient_parser.add_argument('--max-results', type=int, default=5, help='Maximum number of results')
    
    # Recommendations command
    recommend_parser = subparsers.add_parser('recommend', help='Get ingredient recommendations')
    recommend_parser.add_argument('cocktail', help='Name of the cocktail')
    recommend_parser.add_argument('--max-results', type=int, default=5, help='Maximum number of results')
    
    # Details command
    details_parser = subparsers.add_parser('details', help='Show cocktail details')
    details_parser.add_argument('cocktail', help='Name of the cocktail')
    
    args = parser.parse_args()
    
    if args.command == 'similar':
        search_similar_cocktails(args.cocktail, args.max_results)
    elif args.command == 'flavor':
        search_by_flavor(args.description, args.max_results)
    elif args.command == 'ingredients':
        search_by_ingredients(args.ingredients, args.max_results)
    elif args.command == 'recommend':
        get_ingredient_recommendations(args.cocktail, args.max_results)
    elif args.command == 'details':
        show_cocktail_details(args.cocktail)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
