import os
import json
import psycopg2
import openai
import numpy as np
from typing import List, Dict, Optional, Tuple
from sentence_transformers import SentenceTransformer
import logging
from psycopg2.extras import execute_values
import tiktoken

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

COCKTAILS_DIR = "data/cocktails/data/cocktails/"
INGREDIENTS_DIR = "data/cocktails/data/ingredients/"

class CocktailVectorEmbedder:
    def __init__(self, openai_api_key: Optional[str] = None, use_openai: bool = True):
        """
        Initialize the embedder with either OpenAI or SentenceTransformers
        
        Args:
            openai_api_key: OpenAI API key for embeddings
            use_openai: Whether to use OpenAI embeddings (default) or SentenceTransformers
        """
        self.use_openai = use_openai
        
        if use_openai and openai_api_key:
            openai.api_key = openai_api_key
            self.encoding = tiktoken.encoding_for_model("text-embedding-ada-002")
        elif not use_openai:
            # Fallback to SentenceTransformers
            self.model = SentenceTransformer('all-MiniLM-L6-v2')
            logger.info("Using SentenceTransformers model for embeddings")
        else:
            logger.warning("No OpenAI API key provided, falling back to SentenceTransformers")
            self.use_openai = False
            self.model = SentenceTransformer('all-MiniLM-L6-v2')
    
    def get_embedding(self, text: str, max_length: int = 8000) -> List[float]:
        """Get embedding for a text string"""
        if not text or text.strip() == "":
            return None
            
        # Truncate text if too long
        if self.use_openai:
            tokens = self.encoding.encode(text)
            if len(tokens) > max_length:
                tokens = tokens[:max_length]
                text = self.encoding.decode(tokens)
        else:
            # Simple character-based truncation for SentenceTransformers
            if len(text) > max_length:
                text = text[:max_length]
        
        try:
            if self.use_openai:
                response = openai.embeddings.create(
                    input=text,
                    model="text-embedding-ada-002"
                )
                return response.data[0].embedding
            else:
                return self.model.encode(text).tolist()
        except Exception as e:
            logger.error(f"Error generating embedding for text: {str(e)}")
            return None

    def create_flavor_profile_text(self, ingredient: Dict) -> str:
        """Create a comprehensive flavor profile text for an ingredient"""
        flavor_parts = []
        
        if ingredient.get('name'):
            flavor_parts.append(f"Ingredient: {ingredient['name']}")
        
        if ingredient.get('category'):
            flavor_parts.append(f"Category: {ingredient['category']}")
        
        if ingredient.get('description'):
            flavor_parts.append(f"Description: {ingredient['description']}")
        
        if ingredient.get('origin'):
            flavor_parts.append(f"Origin: {ingredient['origin']}")
        
        if ingredient.get('strength'):
            strength = float(ingredient['strength'])
            if strength == 0:
                flavor_parts.append("Non-alcoholic")
            elif strength < 20:
                flavor_parts.append("Low alcohol content")
            elif strength < 40:
                flavor_parts.append("Medium alcohol content")
            else:
                flavor_parts.append("High alcohol content")
        
        # Add flavor descriptors based on category
        category_flavors = {
            'Spirit': 'strong, warming, complex',
            'Liqueur': 'sweet, flavored, aromatic',
            'Citrus juice': 'tart, fresh, acidic, bright',
            'Simple Syrup': 'sweet, smooth, balancing',
            'Bitters': 'bitter, complex, aromatic, balancing',
            'Wine': 'fruity, complex, tannic or crisp',
            'Beer': 'malty, hoppy, refreshing',
            'Vermouth': 'herbal, complex, fortified',
            'Orange Curaçao': 'orange, sweet, citrusy',
            'Tequila': 'agave, earthy, smooth or fiery',
            'Gin': 'botanical, juniper, crisp',
            'Whiskey': 'oaky, vanilla, caramel, warming',
            'Rum': 'molasses, tropical, sweet or spiced',
            'Vodka': 'clean, neutral, smooth'
        }
        
        if ingredient.get('category') in category_flavors:
            flavor_parts.append(f"Flavor profile: {category_flavors[ingredient['category']]}")
        
        return ". ".join(flavor_parts)

    def create_cocktail_flavor_summary(self, cocktail: Dict, ingredients: List[Dict]) -> str:
        """Create a flavor summary for a cocktail based on its ingredients"""
        flavor_parts = []
        
        if cocktail.get('name'):
            flavor_parts.append(f"Cocktail: {cocktail['name']}")
        
        if cocktail.get('description'):
            flavor_parts.append(f"Description: {cocktail['description']}")
        
        if cocktail.get('method'):
            method_descriptions = {
                'Shake': 'shaken for aeration and dilution',
                'Stir': 'stirred for smoothness and clarity',
                'Build': 'built directly for simplicity',
                'Blend': 'blended for creamy texture',
                'Muddle': 'muddled to release essential oils'
            }
            method_desc = method_descriptions.get(cocktail['method'], cocktail['method'])
            flavor_parts.append(f"Preparation: {method_desc}")
        
        if cocktail.get('tags'):
            flavor_parts.append(f"Style: {', '.join(cocktail['tags'])}")
        
        # Ingredient summary
        ingredient_categories = {}
        for ing in ingredients:
            category = ing.get('category', 'Unknown')
            if category not in ingredient_categories:
                ingredient_categories[category] = []
            ingredient_categories[category].append(ing.get('name', ''))
        
        ingredient_summary = []
        for category, names in ingredient_categories.items():
            ingredient_summary.append(f"{category}: {', '.join(names)}")
        
        if ingredient_summary:
            flavor_parts.append(f"Ingredients - {'; '.join(ingredient_summary)}")
        
        return ". ".join(flavor_parts)

    def create_method_description(self, cocktail: Dict) -> str:
        """Create detailed method description"""
        method_details = []
        
        if cocktail.get('method'):
            method_details.append(f"Primary method: {cocktail['method']}")
        
        if cocktail.get('glass'):
            method_details.append(f"Served in: {cocktail['glass']}")
        
        if cocktail.get('garnish'):
            method_details.append(f"Garnished with: {cocktail['garnish']}")
        
        if cocktail.get('instructions'):
            method_details.append(f"Instructions: {cocktail['instructions']}")
        
        return ". ".join(method_details)

def get_all_data_json_paths(root_dir):
    """Get all data.json file paths from subdirectories"""
    paths = []
    if not os.path.exists(root_dir):
        logger.warning(f"Directory does not exist: {root_dir}")
        return paths
        
    for subdir in os.listdir(root_dir):
        full_subdir = os.path.join(root_dir, subdir)
        if os.path.isdir(full_subdir):
            data_json = os.path.join(full_subdir, "data.json")
            if os.path.isfile(data_json):
                paths.append(data_json)
    return paths

def insert_ingredient_with_vectors(cur, ingredient: Dict, embedder: CocktailVectorEmbedder):
    """Insert ingredient with vector embeddings"""
    
    # Generate embeddings
    description_embedding = None
    flavor_profile_embedding = None
    category_embedding = None
    
    if ingredient.get('description'):
        description_embedding = embedder.get_embedding(ingredient['description'])
    
    flavor_profile_text = embedder.create_flavor_profile_text(ingredient)
    if flavor_profile_text:
        flavor_profile_embedding = embedder.get_embedding(flavor_profile_text)
    
    if ingredient.get('category'):
        category_embedding = embedder.get_embedding(ingredient['category'])
    
    cur.execute(
        """
        INSERT INTO ingredients (
            _id, _parent_id, name, strength, description, origin, color, category, 
            created_at, updated_at, images, ingredient_parts, prices, calculator_id, 
            sugar_g_per_ml, acidity, distillery, units,
            description_embedding, flavor_profile_embedding, category_embedding
        ) VALUES (
            %(id)s, %(parent_id)s, %(name)s, %(strength)s, %(description)s, %(origin)s, 
            %(color)s, %(category)s, %(created_at)s, %(updated_at)s, %(images)s, 
            %(ingredient_parts)s, %(prices)s, %(calculator_id)s, %(sugar_g_per_ml)s, 
            %(acidity)s, %(distillery)s, %(units)s,
            %(description_embedding)s, %(flavor_profile_embedding)s, %(category_embedding)s
        ) ON CONFLICT (_id) DO UPDATE SET
            name = EXCLUDED.name,
            strength = EXCLUDED.strength,
            description = EXCLUDED.description,
            origin = EXCLUDED.origin,
            color = EXCLUDED.color,
            category = EXCLUDED.category,
            description_embedding = EXCLUDED.description_embedding,
            flavor_profile_embedding = EXCLUDED.flavor_profile_embedding,
            category_embedding = EXCLUDED.category_embedding,
            updated_at_db = CURRENT_TIMESTAMP;
        """,
        {
            "id": ingredient.get("_id"),
            "parent_id": ingredient.get("_parent_id"),
            "name": ingredient.get("name"),
            "strength": ingredient.get("strength"),
            "description": ingredient.get("description"),
            "origin": ingredient.get("origin"),
            "color": ingredient.get("color"),
            "category": ingredient.get("category"),
            "created_at": ingredient.get("created_at"),
            "updated_at": ingredient.get("updated_at"),
            "images": json.dumps(ingredient.get("images")) if ingredient.get("images") else None,
            "ingredient_parts": json.dumps(ingredient.get("ingredient_parts")) if ingredient.get("ingredient_parts") else None,
            "prices": json.dumps(ingredient.get("prices")) if ingredient.get("prices") else None,
            "calculator_id": ingredient.get("calculator_id"),
            "sugar_g_per_ml": ingredient.get("sugar_g_per_ml"),
            "acidity": ingredient.get("acidity"),
            "distillery": ingredient.get("distillery"),
            "units": ingredient.get("units"),
            "description_embedding": description_embedding,
            "flavor_profile_embedding": flavor_profile_embedding,
            "category_embedding": category_embedding,
        },
    )

def insert_cocktail_with_vectors(cur, cocktail: Dict, embedder: CocktailVectorEmbedder):
    """Insert cocktail with vector embeddings"""
    
    # Get ingredient details for this cocktail
    ingredients = cocktail.get('ingredients', [])
    
    # Generate embeddings
    description_embedding = None
    flavor_embedding = None
    method_embedding = None
    ingredient_summary_embedding = None
    tags_embedding = None
    
    if cocktail.get('description'):
        description_embedding = embedder.get_embedding(cocktail['description'])
    
    # Create comprehensive flavor profile
    flavor_summary = embedder.create_cocktail_flavor_summary(cocktail, ingredients)
    if flavor_summary:
        flavor_embedding = embedder.get_embedding(flavor_summary)
    
    # Method embedding
    method_description = embedder.create_method_description(cocktail)
    if method_description:
        method_embedding = embedder.get_embedding(method_description)
    
    # Ingredient summary embedding
    ingredient_names = [ing.get('name', '') for ing in ingredients if ing.get('name')]
    if ingredient_names:
        ingredient_summary = f"Contains: {', '.join(ingredient_names)}"
        ingredient_summary_embedding = embedder.get_embedding(ingredient_summary)
    
    # Tags embedding
    if cocktail.get('tags'):
        tags_text = ', '.join(cocktail['tags'])
        tags_embedding = embedder.get_embedding(tags_text)
    
    # Insert cocktail
    cur.execute(
        """
        INSERT INTO cocktails (
            _id, name, instructions, created_at, updated_at, description, source, 
            garnish, abv, tags, glass, method, utensils, images, parent_cocktail_id, year,
            description_embedding, flavor_embedding, method_embedding, 
            ingredient_summary_embedding, tags_embedding
        ) VALUES (
            %(id)s, %(name)s, %(instructions)s, %(created_at)s, %(updated_at)s, 
            %(description)s, %(source)s, %(garnish)s, %(abv)s, %(tags)s, %(glass)s, 
            %(method)s, %(utensils)s, %(images)s, %(parent_cocktail_id)s, %(year)s,
            %(description_embedding)s, %(flavor_embedding)s, %(method_embedding)s,
            %(ingredient_summary_embedding)s, %(tags_embedding)s
        ) ON CONFLICT (_id) DO UPDATE SET
            name = EXCLUDED.name,
            instructions = EXCLUDED.instructions,
            description = EXCLUDED.description,
            description_embedding = EXCLUDED.description_embedding,
            flavor_embedding = EXCLUDED.flavor_embedding,
            method_embedding = EXCLUDED.method_embedding,
            ingredient_summary_embedding = EXCLUDED.ingredient_summary_embedding,
            tags_embedding = EXCLUDED.tags_embedding,
            updated_at_db = CURRENT_TIMESTAMP
        RETURNING id;
        """,
        {
            "id": cocktail.get("_id"),
            "name": cocktail.get("name"),
            "instructions": cocktail.get("instructions"),
            "created_at": cocktail.get("created_at"),
            "updated_at": cocktail.get("updated_at"),
            "description": cocktail.get("description"),
            "source": cocktail.get("source"),
            "garnish": cocktail.get("garnish"),
            "abv": cocktail.get("abv"),
            "tags": cocktail.get("tags"),
            "glass": cocktail.get("glass"),
            "method": cocktail.get("method"),
            "utensils": cocktail.get("utensils"),
            "images": json.dumps(cocktail.get("images")) if cocktail.get("images") else None,
            "parent_cocktail_id": cocktail.get("parent_cocktail_id"),
            "year": cocktail.get("year"),
            "description_embedding": description_embedding,
            "flavor_embedding": flavor_embedding,
            "method_embedding": method_embedding,
            "ingredient_summary_embedding": ingredient_summary_embedding,
            "tags_embedding": tags_embedding,
        },
    )
    
    # Get the cocktail ID
    cocktail_db_id = cur.fetchone()[0]
    
    # Insert cocktail-ingredient relationships
    for ing in ingredients:
        if ing.get('_id'):
            # Get ingredient database ID
            cur.execute("SELECT id FROM ingredients WHERE _id = %s", (ing['_id'],))
            ingredient_result = cur.fetchone()
            
            if ingredient_result:
                ingredient_db_id = ingredient_result[0]
                
                cur.execute(
                    """
                    INSERT INTO cocktail_ingredients (
                        cocktail_id, ingredient_id, amount, units, optional, 
                        amount_max, note, sort_order, is_specified, substitutes
                    ) VALUES (
                        %(cocktail_id)s, %(ingredient_id)s, %(amount)s, %(units)s, 
                        %(optional)s, %(amount_max)s, %(note)s, %(sort_order)s, 
                        %(is_specified)s, %(substitutes)s
                    ) ON CONFLICT (cocktail_id, ingredient_id, sort_order) DO NOTHING;
                    """,
                    {
                        "cocktail_id": cocktail_db_id,
                        "ingredient_id": ingredient_db_id,
                        "amount": ing.get("amount"),
                        "units": ing.get("units"),
                        "optional": ing.get("optional", False),
                        "amount_max": ing.get("amount_max"),
                        "note": ing.get("note"),
                        "sort_order": ing.get("sort", 0),
                        "is_specified": ing.get("is_specified", False),
                        "substitutes": json.dumps(ing.get("substitutes")) if ing.get("substitutes") else None,
                    }
                )

def main():
    """Main function to load and embed all cocktail data"""
    # Initialize embedder
    openai_api_key = os.getenv('OPENAI_API_KEY')
    embedder = CocktailVectorEmbedder(openai_api_key=openai_api_key)
    
    # Database connection
    db_config = {
        'host': os.getenv('DB_HOST', 'localhost'),
        'database': os.getenv('DB_NAME', 'agenticbeerathon'),
        'user': os.getenv('DB_USER', 'postgres'),
        'password': os.getenv('DB_PASSWORD', ''),
        'port': os.getenv('DB_PORT', '5432')
    }
    
    conn = psycopg2.connect(**db_config)
    cur = conn.cursor()
    
    try:
        # Process ingredients first
        logger.info("Processing ingredients...")
        ingredient_paths = get_all_data_json_paths(INGREDIENTS_DIR)
        
        for i, path in enumerate(ingredient_paths):
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    ingredient = json.load(f)
                    insert_ingredient_with_vectors(cur, ingredient, embedder)
                
                if (i + 1) % 10 == 0:
                    logger.info(f"Processed {i + 1}/{len(ingredient_paths)} ingredients")
                    conn.commit()
                    
            except Exception as e:
                logger.error(f"Error processing ingredient {path}: {str(e)}")
                continue
        
        conn.commit()
        logger.info(f"Completed processing {len(ingredient_paths)} ingredients")
        
        # Process cocktails
        logger.info("Processing cocktails...")
        cocktail_paths = get_all_data_json_paths(COCKTAILS_DIR)
        
        for i, path in enumerate(cocktail_paths):
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    cocktail = json.load(f)
                    insert_cocktail_with_vectors(cur, cocktail, embedder)
                
                if (i + 1) % 10 == 0:
                    logger.info(f"Processed {i + 1}/{len(cocktail_paths)} cocktails")
                    conn.commit()
                    
            except Exception as e:
                logger.error(f"Error processing cocktail {path}: {str(e)}")
                continue
        
        conn.commit()
        logger.info(f"Completed processing {len(cocktail_paths)} cocktails")
        
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        conn.rollback()
        raise
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    main()
