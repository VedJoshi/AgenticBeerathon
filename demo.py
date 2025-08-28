#!/usr/bin/env python3
"""
Demo script showing vector search capabilities
"""

import os
import sys
import json

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

def demo_vector_search():
    """Demonstrate vector search functionality"""
    
    print("🍸 AgenticBeerathon Vector Database Demo")
    print("=" * 50)
    
    # Database configuration
    db_config = {
        'host': os.getenv('DB_HOST', 'localhost'),
        'database': os.getenv('DB_NAME', 'agenticbeerathon'),
        'user': os.getenv('DB_USER', 'postgres'),
        'password': os.getenv('DB_PASSWORD', ''),
        'port': int(os.getenv('DB_PORT', '5432'))
    }
    
    try:
        # Test database connection
        print("🔍 Testing database connection...")
        from src.utils.database_config import DatabaseConfig
        
        config = DatabaseConfig()
        if config.test_connection():
            print("✅ Database connection successful!")
        else:
            print("❌ Database connection failed!")
            print("Please check your database configuration in .env file")
            return
        
        # Initialize search API
        from src.utils.vector_search_api import create_search_api
        search_api = create_search_api(db_config)
        
        print("\n📊 Database Statistics:")
        print("-" * 30)
        
        # Get counts
        import psycopg2
        conn = psycopg2.connect(**db_config)
        cur = conn.cursor()
        
        cur.execute("SELECT COUNT(*) FROM cocktails")
        cocktail_count = cur.fetchone()[0]
        
        cur.execute("SELECT COUNT(*) FROM ingredients")
        ingredient_count = cur.fetchone()[0]
        
        cur.execute("SELECT COUNT(*) FROM cocktail_ingredients")
        relationship_count = cur.fetchone()[0]
        
        print(f"Cocktails: {cocktail_count}")
        print(f"Ingredients: {ingredient_count}")
        print(f"Relationships: {relationship_count}")
        
        # Test vector search if data exists
        if cocktail_count > 0:
            print("\n🔍 Vector Search Examples:")
            print("-" * 30)
            
            # Example 1: Find similar cocktails to Margarita
            print("\n1. Finding cocktails similar to 'Margarita':")
            try:
                similar = search_api.find_similar_cocktails_by_flavor("Margarita", max_results=3)
                if similar:
                    for i, match in enumerate(similar[:3], 1):
                        print(f"   {i}. {match.cocktail_name} ({match.similarity_score:.1%} similar)")
                else:
                    print("   No similar cocktails found (may need embeddings)")
            except Exception as e:
                print(f"   Error: {e}")
            
            # Example 2: Search by ingredients
            print("\n2. Finding cocktails with 'gin' and 'lime':")
            try:
                ingredient_matches = search_api.find_cocktails_by_ingredient_similarity(
                    ["gin", "lime"], 
                    similarity_threshold=0.3,
                    max_results=3
                )
                if ingredient_matches:
                    for i, match in enumerate(ingredient_matches[:3], 1):
                        print(f"   {i}. {match['cocktail_name']} ({match['match_percentage']:.1%} match)")
                else:
                    print("   No matches found")
            except Exception as e:
                print(f"   Error: {e}")
            
            # Example 3: Cocktail preferences
            print("\n3. Low-alcohol cocktails (ABV < 15%):")
            try:
                low_alcohol = search_api.find_cocktails_by_preferences(
                    preferred_strength_min=0,
                    preferred_strength_max=15,
                    max_results=3
                )
                if low_alcohol:
                    for i, match in enumerate(low_alcohol[:3], 1):
                        abv_str = f"{match['abv']}%" if match['abv'] else "N/A"
                        print(f"   {i}. {match['cocktail_name']} (ABV: {abv_str})")
                else:
                    print("   No matches found")
            except Exception as e:
                print(f"   Error: {e}")
        
        else:
            print("\n⚠️  No cocktail data found in database.")
            print("Run: python src/utils/cocktail_data_embedder.py")
        
        cur.close()
        conn.close()
        
        print("\n🎉 Demo completed!")
        print("\nNext steps:")
        print("1. Load data: python src/utils/cocktail_data_embedder.py")
        print("2. Try CLI: python tools/cocktail_search_cli.py similar Margarita")
        print("3. Check README: VECTOR_DATABASE_README.md")
        
    except ImportError as e:
        print(f"❌ Missing dependencies: {e}")
        print("Please install requirements: pip install -r requirements.txt")
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        print("Please check your setup and try again.")

if __name__ == "__main__":
    demo_vector_search()
