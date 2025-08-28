"""
Vector search API for cocktail recommendations
"""

import json
import logging
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
import numpy as np

logger = logging.getLogger(__name__)

@dataclass
class CocktailMatch:
    """Represents a cocktail match from vector search"""
    cocktail_id: int
    cocktail_name: str
    similarity_score: float
    description: str
    abv: Optional[float]
    method: Optional[str]
    glass: Optional[str]
    tags: Optional[List[str]]

@dataclass
class IngredientMatch:
    """Represents an ingredient match from vector search"""
    ingredient_id: int
    ingredient_name: str
    similarity_score: float
    category: str
    description: str
    strength: Optional[float]

class CocktailVectorSearch:
    """Vector search interface for cocktail recommendations"""
    
    def __init__(self, db_config):
        self.db_config = db_config
        
    def get_connection(self):
        """Get database connection - to be implemented based on your DB setup"""
        try:
            import psycopg2
            return psycopg2.connect(**self.db_config)
        except ImportError:
            logger.error("psycopg2 not installed. Please install required dependencies.")
            raise
    
    def find_similar_cocktails_by_flavor(
        self, 
        cocktail_name: str, 
        max_results: int = 10,
        similarity_threshold: float = 0.7
    ) -> List[CocktailMatch]:
        """Find cocktails similar to a given cocktail by flavor profile"""
        
        conn = self.get_connection()
        cur = conn.cursor()
        
        try:
            # Get cocktail ID
            cur.execute("SELECT id FROM cocktails WHERE name ILIKE %s LIMIT 1", (f"%{cocktail_name}%",))
            result = cur.fetchone()
            
            if not result:
                logger.warning(f"Cocktail '{cocktail_name}' not found")
                return []
            
            cocktail_id = result[0]
            
            # Find similar cocktails
            cur.execute(
                "SELECT * FROM find_similar_cocktails_by_flavor(%s, %s, %s)",
                (cocktail_id, similarity_threshold, max_results)
            )
            
            results = cur.fetchall()
            matches = []
            
            for row in results:
                match = CocktailMatch(
                    cocktail_id=row[0],
                    cocktail_name=row[1],
                    similarity_score=float(row[2]),
                    description=row[3] or "",
                    abv=float(row[4]) if row[4] else None,
                    method=row[5],
                    glass=row[6],
                    tags=None
                )
                matches.append(match)
            
            return matches
            
        except Exception as e:
            logger.error(f"Error finding similar cocktails: {e}")
            return []
        finally:
            cur.close()
            conn.close()
    
    def search_cocktails_by_flavor_description(
        self,
        flavor_description: str,
        max_results: int = 10,
        similarity_threshold: float = 0.5
    ) -> List[CocktailMatch]:
        """Search cocktails by flavor description using embeddings"""
        
        try:
            # You would need to generate embedding for the flavor description
            # This is a placeholder - you'd need the actual embedding service
            from src.utils.cocktail_data_embedder import CocktailVectorEmbedder
            
            embedder = CocktailVectorEmbedder()
            flavor_embedding = embedder.get_embedding(flavor_description)
            
            if not flavor_embedding:
                logger.error("Could not generate embedding for flavor description")
                return []
            
            conn = self.get_connection()
            cur = conn.cursor()
            
            cur.execute(
                "SELECT * FROM search_cocktails_by_flavor_text(%s, %s, %s, %s)",
                (flavor_description, flavor_embedding, max_results, similarity_threshold)
            )
            
            results = cur.fetchall()
            matches = []
            
            for row in results:
                match = CocktailMatch(
                    cocktail_id=row[0],
                    cocktail_name=row[1],
                    similarity_score=float(row[2]),
                    description=row[3] or "",
                    abv=None,
                    method=row[5],
                    glass=None,
                    tags=row[4] if row[4] else []
                )
                matches.append(match)
            
            return matches
            
        except Exception as e:
            logger.error(f"Error searching cocktails by flavor: {e}")
            return []
        finally:
            if 'cur' in locals():
                cur.close()
            if 'conn' in locals():
                conn.close()
    
    def find_cocktails_by_ingredient_similarity(
        self,
        ingredients: List[str],
        similarity_threshold: float = 0.6,
        max_results: int = 15
    ) -> List[Dict]:
        """Find cocktails with similar ingredients"""
        
        conn = self.get_connection()
        cur = conn.cursor()
        
        try:
            cur.execute(
                "SELECT * FROM find_cocktails_by_ingredient_similarity(%s, %s, %s)",
                (ingredients, similarity_threshold, max_results)
            )
            
            results = cur.fetchall()
            matches = []
            
            for row in results:
                match = {
                    'cocktail_id': row[0],
                    'cocktail_name': row[1],
                    'matching_ingredients': row[2],
                    'total_ingredients': row[3],
                    'match_percentage': float(row[4]),
                    'description': row[5] or ""
                }
                matches.append(match)
            
            return matches
            
        except Exception as e:
            logger.error(f"Error finding cocktails by ingredients: {e}")
            return []
        finally:
            cur.close()
            conn.close()
    
    def get_ingredient_recommendations(
        self,
        cocktail_name: str,
        max_results: int = 10
    ) -> List[IngredientMatch]:
        """Get ingredient recommendations based on a cocktail"""
        
        conn = self.get_connection()
        cur = conn.cursor()
        
        try:
            # Get cocktail ID
            cur.execute("SELECT id FROM cocktails WHERE name ILIKE %s LIMIT 1", (f"%{cocktail_name}%",))
            result = cur.fetchone()
            
            if not result:
                logger.warning(f"Cocktail '{cocktail_name}' not found")
                return []
            
            cocktail_id = result[0]
            
            cur.execute(
                "SELECT * FROM get_ingredient_recommendations(%s, %s)",
                (cocktail_id, max_results)
            )
            
            results = cur.fetchall()
            matches = []
            
            for row in results:
                match = IngredientMatch(
                    ingredient_id=row[0],
                    ingredient_name=row[1],
                    similarity_score=float(row[3]),
                    category=row[2] or "",
                    description=row[4] or "",
                    strength=float(row[5]) if row[5] else None
                )
                matches.append(match)
            
            return matches
            
        except Exception as e:
            logger.error(f"Error getting ingredient recommendations: {e}")
            return []
        finally:
            cur.close()
            conn.close()
    
    def find_cocktails_by_preferences(
        self,
        preferred_strength_min: float = 0,
        preferred_strength_max: float = 50,
        excluded_categories: List[str] = None,
        required_tags: List[str] = None,
        max_results: int = 15
    ) -> List[Dict]:
        """Find cocktails based on preferences and restrictions"""
        
        if excluded_categories is None:
            excluded_categories = []
        if required_tags is None:
            required_tags = []
        
        conn = self.get_connection()
        cur = conn.cursor()
        
        try:
            cur.execute(
                "SELECT * FROM find_cocktails_by_preferences(%s, %s, %s, %s, %s)",
                (preferred_strength_min, preferred_strength_max, excluded_categories, 
                 required_tags, max_results)
            )
            
            results = cur.fetchall()
            matches = []
            
            for row in results:
                match = {
                    'cocktail_id': row[0],
                    'cocktail_name': row[1],
                    'abv': float(row[2]) if row[2] else None,
                    'description': row[3] or "",
                    'method': row[4],
                    'tags': row[5] if row[5] else []
                }
                matches.append(match)
            
            return matches
            
        except Exception as e:
            logger.error(f"Error finding cocktails by preferences: {e}")
            return []
        finally:
            cur.close()
            conn.close()
    
    def get_cocktail_details(self, cocktail_id: int) -> Optional[Dict]:
        """Get detailed information about a specific cocktail"""
        
        conn = self.get_connection()
        cur = conn.cursor()
        
        try:
            # Get cocktail details
            cur.execute("""
                SELECT c.*, 
                       array_agg(
                           json_build_object(
                               'name', i.name,
                               'amount', ci.amount,
                               'units', ci.units,
                               'category', i.category,
                               'optional', ci.optional,
                               'note', ci.note
                           ) ORDER BY ci.sort_order
                       ) as ingredients
                FROM cocktails c
                LEFT JOIN cocktail_ingredients ci ON c.id = ci.cocktail_id
                LEFT JOIN ingredients i ON ci.ingredient_id = i.id
                WHERE c.id = %s
                GROUP BY c.id
            """, (cocktail_id,))
            
            result = cur.fetchone()
            
            if not result:
                return None
            
            # Parse the result into a dictionary
            cocktail = {
                'id': result[0],
                '_id': result[1],
                'name': result[2],
                'instructions': result[3],
                'description': result[7],
                'source': result[8],
                'garnish': result[9],
                'abv': float(result[10]) if result[10] else None,
                'tags': result[11] if result[11] else [],
                'glass': result[12],
                'method': result[13],
                'utensils': result[14] if result[14] else [],
                'ingredients': result[-1] if result[-1] else []
            }
            
            return cocktail
            
        except Exception as e:
            logger.error(f"Error getting cocktail details: {e}")
            return None
        finally:
            cur.close()
            conn.close()


def create_search_api(db_config: Dict) -> CocktailVectorSearch:
    """Factory function to create a CocktailVectorSearch instance"""
    return CocktailVectorSearch(db_config)
