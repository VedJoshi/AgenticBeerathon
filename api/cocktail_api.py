"""
FastAPI server for cocktail vector search
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
import os
import sys
from pydantic import BaseModel

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

app = FastAPI(
    title="Cocktail Vector Search API",
    description="AI-powered cocktail recommendations using vector similarity search",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database configuration
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'database': os.getenv('DB_NAME', 'agenticbeerathon'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', ''),
    'port': int(os.getenv('DB_PORT', '5432'))
}

# Initialize search API
try:
    from src.utils.vector_search_api import create_search_api
    search_api = create_search_api(DB_CONFIG)
except ImportError:
    search_api = None

# Pydantic models
class CocktailMatch(BaseModel):
    cocktail_id: int
    cocktail_name: str
    similarity_score: float
    description: str
    abv: Optional[float]
    method: Optional[str]
    glass: Optional[str]
    tags: Optional[List[str]]

class IngredientMatch(BaseModel):
    ingredient_id: int
    ingredient_name: str
    similarity_score: float
    category: str
    description: str
    strength: Optional[float]

class CocktailDetails(BaseModel):
    id: int
    name: str
    description: Optional[str]
    instructions: Optional[str]
    method: Optional[str]
    glass: Optional[str]
    abv: Optional[float]
    garnish: Optional[str]
    tags: Optional[List[str]]
    ingredients: List[dict]

class SearchResponse(BaseModel):
    query: str
    results: List[dict]
    total_found: int

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Cocktail Vector Search API",
        "version": "1.0.0",
        "endpoints": {
            "similar": "/cocktails/similar/{cocktail_name}",
            "flavor_search": "/cocktails/search/flavor",
            "ingredient_search": "/cocktails/search/ingredients",
            "recommendations": "/cocktails/{cocktail_name}/recommendations",
            "details": "/cocktails/{cocktail_id}/details",
            "preferences": "/cocktails/search/preferences"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    if not search_api:
        raise HTTPException(status_code=503, detail="Search API not available")
    
    try:
        from src.utils.database_config import DatabaseConfig
        config = DatabaseConfig()
        if config.test_connection():
            return {"status": "healthy", "database": "connected"}
        else:
            return {"status": "unhealthy", "database": "disconnected"}
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Health check failed: {str(e)}")

@app.get("/cocktails/similar/{cocktail_name}")
async def find_similar_cocktails(
    cocktail_name: str,
    max_results: int = Query(10, ge=1, le=50),
    threshold: float = Query(0.6, ge=0.0, le=1.0)
):
    """Find cocktails similar to the given cocktail"""
    if not search_api:
        raise HTTPException(status_code=503, detail="Search API not available")
    
    try:
        results = search_api.find_similar_cocktails_by_flavor(
            cocktail_name, 
            max_results=max_results,
            similarity_threshold=threshold
        )
        
        return {
            "query": cocktail_name,
            "results": [
                {
                    "cocktail_id": r.cocktail_id,
                    "cocktail_name": r.cocktail_name,
                    "similarity_score": r.similarity_score,
                    "description": r.description,
                    "abv": r.abv,
                    "method": r.method,
                    "glass": r.glass
                }
                for r in results
            ],
            "total_found": len(results)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/cocktails/search/flavor")
async def search_by_flavor(
    description: str = Query(..., description="Flavor description to search for"),
    max_results: int = Query(10, ge=1, le=50),
    threshold: float = Query(0.5, ge=0.0, le=1.0)
):
    """Search cocktails by flavor description"""
    if not search_api:
        raise HTTPException(status_code=503, detail="Search API not available")
    
    try:
        results = search_api.search_cocktails_by_flavor_description(
            description,
            max_results=max_results,
            similarity_threshold=threshold
        )
        
        return {
            "query": description,
            "results": [
                {
                    "cocktail_id": r.cocktail_id,
                    "cocktail_name": r.cocktail_name,
                    "similarity_score": r.similarity_score,
                    "description": r.description,
                    "method": r.method,
                    "tags": r.tags
                }
                for r in results
            ],
            "total_found": len(results)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/cocktails/search/ingredients")
async def search_by_ingredients(
    ingredients: str = Query(..., description="Comma-separated list of ingredients"),
    max_results: int = Query(15, ge=1, le=50),
    threshold: float = Query(0.3, ge=0.0, le=1.0)
):
    """Search cocktails by ingredients"""
    if not search_api:
        raise HTTPException(status_code=503, detail="Search API not available")
    
    try:
        ingredient_list = [ing.strip() for ing in ingredients.split(',')]
        results = search_api.find_cocktails_by_ingredient_similarity(
            ingredient_list,
            similarity_threshold=threshold,
            max_results=max_results
        )
        
        return {
            "query": ingredient_list,
            "results": results,
            "total_found": len(results)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/cocktails/{cocktail_name}/recommendations")
async def get_ingredient_recommendations(
    cocktail_name: str,
    max_results: int = Query(10, ge=1, le=50)
):
    """Get ingredient recommendations for a cocktail"""
    if not search_api:
        raise HTTPException(status_code=503, detail="Search API not available")
    
    try:
        results = search_api.get_ingredient_recommendations(
            cocktail_name,
            max_results=max_results
        )
        
        return {
            "cocktail": cocktail_name,
            "recommendations": [
                {
                    "ingredient_id": r.ingredient_id,
                    "ingredient_name": r.ingredient_name,
                    "similarity_score": r.similarity_score,
                    "category": r.category,
                    "description": r.description,
                    "strength": r.strength
                }
                for r in results
            ],
            "total_found": len(results)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/cocktails/{cocktail_id}/details")
async def get_cocktail_details(cocktail_id: int):
    """Get detailed information about a cocktail"""
    if not search_api:
        raise HTTPException(status_code=503, detail="Search API not available")
    
    try:
        details = search_api.get_cocktail_details(cocktail_id)
        
        if not details:
            raise HTTPException(status_code=404, detail="Cocktail not found")
        
        return details
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/cocktails/search/preferences")
async def search_by_preferences(
    min_abv: float = Query(0, ge=0, le=100),
    max_abv: float = Query(50, ge=0, le=100),
    excluded_categories: Optional[str] = Query(None, description="Comma-separated list of categories to exclude"),
    required_tags: Optional[str] = Query(None, description="Comma-separated list of required tags"),
    max_results: int = Query(15, ge=1, le=50)
):
    """Search cocktails based on preferences and restrictions"""
    if not search_api:
        raise HTTPException(status_code=503, detail="Search API not available")
    
    try:
        excluded_list = [cat.strip() for cat in excluded_categories.split(',')] if excluded_categories else []
        required_list = [tag.strip() for tag in required_tags.split(',')] if required_tags else []
        
        results = search_api.find_cocktails_by_preferences(
            preferred_strength_min=min_abv,
            preferred_strength_max=max_abv,
            excluded_categories=excluded_list,
            required_tags=required_list,
            max_results=max_results
        )
        
        return {
            "preferences": {
                "min_abv": min_abv,
                "max_abv": max_abv,
                "excluded_categories": excluded_list,
                "required_tags": required_list
            },
            "results": results,
            "total_found": len(results)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/stats")
async def get_database_stats():
    """Get database statistics"""
    if not search_api:
        raise HTTPException(status_code=503, detail="Search API not available")
    
    try:
        import psycopg2
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        
        # Get counts
        cur.execute("SELECT COUNT(*) FROM cocktails")
        cocktail_count = cur.fetchone()[0]
        
        cur.execute("SELECT COUNT(*) FROM ingredients")
        ingredient_count = cur.fetchone()[0]
        
        cur.execute("SELECT COUNT(*) FROM cocktail_ingredients")
        relationship_count = cur.fetchone()[0]
        
        # Get embeddings stats
        cur.execute("SELECT COUNT(*) FROM cocktails WHERE flavor_embedding IS NOT NULL")
        cocktails_with_embeddings = cur.fetchone()[0]
        
        cur.execute("SELECT COUNT(*) FROM ingredients WHERE description_embedding IS NOT NULL")
        ingredients_with_embeddings = cur.fetchone()[0]
        
        cur.close()
        conn.close()
        
        return {
            "cocktails": {
                "total": cocktail_count,
                "with_embeddings": cocktails_with_embeddings
            },
            "ingredients": {
                "total": ingredient_count,
                "with_embeddings": ingredients_with_embeddings
            },
            "relationships": relationship_count,
            "embedding_coverage": {
                "cocktails": f"{(cocktails_with_embeddings/cocktail_count*100):.1f}%" if cocktail_count > 0 else "0%",
                "ingredients": f"{(ingredients_with_embeddings/ingredient_count*100):.1f}%" if ingredient_count > 0 else "0%"
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
