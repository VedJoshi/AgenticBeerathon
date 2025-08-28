# AgenticBeerathon Vector Database

This project implements a pgvector-powered database for storing and searching cocktail data using semantic embeddings. It enables intelligent cocktail recommendations based on flavor profiles, ingredients, and preparation methods.

## 🚀 Features

- **Vector Search**: Find similar cocktails based on flavor profiles using semantic embeddings
- **Ingredient Matching**: Discover cocktails with similar ingredients
- **Flavor Search**: Search cocktails by natural language flavor descriptions
- **Smart Recommendations**: Get ingredient suggestions based on existing cocktails
- **Preference Filtering**: Find cocktails matching dietary restrictions and preferences

## 🏗️ Architecture

### Database Schema
- **PostgreSQL** with **pgvector** extension for vector similarity search
- **Normalized tables**: `cocktails`, `ingredients`, `cocktail_ingredients`
- **Vector embeddings**: Multiple embedding types per entity for different search scenarios

### Vector Embeddings
Each cocktail and ingredient has multiple vector embeddings:

**Cocktails:**
- `description_embedding`: Full description
- `flavor_embedding`: Combined flavor profile from ingredients
- `method_embedding`: Preparation method details
- `ingredient_summary_embedding`: Summary of all ingredients
- `tags_embedding`: Style and category tags

**Ingredients:**
- `description_embedding`: Ingredient description
- `flavor_profile_embedding`: Comprehensive flavor characteristics
- `category_embedding`: Category-based grouping

## 📊 Database Structure

```sql
-- Main tables
cocktails (id, name, description, instructions, method, glass, abv, tags, ...)
ingredients (id, name, category, strength, description, origin, ...)
cocktail_ingredients (cocktail_id, ingredient_id, amount, units, ...)

-- Vector columns (1536 dimensions for OpenAI embeddings)
cocktails.*_embedding vector(1536)
ingredients.*_embedding vector(1536)

-- Vector search indexes
CREATE INDEX ON cocktails USING ivfflat (flavor_embedding vector_cosine_ops);
```

## 🛠️ Setup

### Prerequisites
- PostgreSQL 12+ with pgvector extension
- Python 3.8+
- OpenAI API key (optional, for better embeddings)

### Quick Start

1. **Run the setup script:**
   ```bash
   chmod +x setup.sh
   ./setup.sh
   ```

2. **Update configuration:**
   Edit `.env` file with your database credentials and API keys

3. **Load cocktail data:**
   ```bash
   source venv/bin/activate
   python src/utils/cocktail_data_embedder.py
   ```

4. **Test the search:**
   ```bash
   python tools/cocktail_search_cli.py similar Margarita
   ```

### Manual Setup

1. **Install PostgreSQL and pgvector:**
   ```bash
   # macOS
   brew install postgresql pgvector
   
   # Ubuntu
   sudo apt-get install postgresql postgresql-contrib
   sudo apt install postgresql-14-pgvector
   ```

2. **Create database:**
   ```bash
   createdb agenticbeerathon
   psql -d agenticbeerathon -c "CREATE EXTENSION vector;"
   ```

3. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up database schema:**
   ```bash
   psql -d agenticbeerathon -f database/schema.sql
   psql -d agenticbeerathon -f database/vector_functions.sql
   ```

## 🔍 Usage

### Command Line Interface

```bash
# Find cocktails similar to Margarita
python tools/cocktail_search_cli.py similar Margarita --max-results 5

# Search by flavor description
python tools/cocktail_search_cli.py flavor "citrusy and refreshing" --max-results 5

# Find cocktails with specific ingredients
python tools/cocktail_search_cli.py ingredients gin lime juice --max-results 5

# Get ingredient recommendations for a cocktail
python tools/cocktail_search_cli.py recommend "Old Fashioned" --max-results 5

# Show detailed cocktail information
python tools/cocktail_search_cli.py details Negroni
```

### Python API

```python
from src.utils.vector_search_api import create_search_api

# Initialize search API
db_config = {
    'host': 'localhost',
    'database': 'agenticbeerathon',
    'user': 'postgres',
    'password': '',
    'port': 5432
}
search_api = create_search_api(db_config)

# Find similar cocktails
similar = search_api.find_similar_cocktails_by_flavor("Margarita", max_results=5)

# Search by flavor description
matches = search_api.search_cocktails_by_flavor_description(
    "sweet and fruity with tropical notes", 
    max_results=10
)

# Find cocktails with similar ingredients
ingredient_matches = search_api.find_cocktails_by_ingredient_similarity(
    ["gin", "lime juice", "simple syrup"],
    similarity_threshold=0.6
)
```

## 🔧 Database Functions

The system includes several PostgreSQL functions for vector search:

- `find_similar_cocktails_by_flavor(cocktail_id, threshold, max_results)`
- `search_cocktails_by_flavor_text(description, embedding, max_results, threshold)`
- `find_cocktails_by_ingredient_similarity(ingredients[], threshold, max_results)`
- `get_ingredient_recommendations(cocktail_id, max_results)`
- `find_cocktails_by_preferences(min_abv, max_abv, excluded_categories[], required_tags[], max_results)`

## 📈 Performance

- **Vector Indexes**: IVFFlat indexes with 100 lists for sub-second search
- **Embedding Dimensions**: 1536 (OpenAI) or 384 (SentenceTransformers)
- **Search Speed**: <100ms for most queries on 500+ cocktails
- **Similarity Metrics**: Cosine similarity for semantic matching

## 🔄 Data Processing

### Embedding Generation
1. **Ingredients**: Combine name, category, description, origin, and strength into flavor profiles
2. **Cocktails**: Create comprehensive flavor summaries from ingredients, method, and description
3. **Fallback**: SentenceTransformers model if OpenAI API unavailable

### Flavor Profile Creation
```python
# Example flavor profile for an ingredient
"Ingredient: Gin. Category: Spirit. Description: A spirit flavored with botanicals. 
Origin: England. Flavor profile: botanical, juniper, crisp. High alcohol content."

# Example cocktail flavor summary
"Cocktail: Negroni. Description: A bitter Italian aperitif. Preparation: stirred for smoothness. 
Style: Classic, Bitter. Ingredients - Spirit: Gin; Liqueur: Campari; Vermouth: Sweet Vermouth."
```

## 🚦 Environment Variables

```bash
# Database
DB_HOST=localhost
DB_NAME=agenticbeerathon
DB_USER=postgres
DB_PASSWORD=your_password
DB_PORT=5432

# OpenAI (optional)
OPENAI_API_KEY=your_openai_key

# AWS (if using)
AWS_REGION=us-east-1
BEDROCK_MODEL_ID=anthropic.claude-3-sonnet-20240229-v1:0
```

## 🧪 Testing

```bash
# Test database connection
python -c "from src.utils.database_config import DatabaseConfig; print('✅ Connected' if DatabaseConfig().test_connection() else '❌ Failed')"

# Test search functionality
python tools/cocktail_search_cli.py similar Martini --max-results 3
```

## 🛣️ Roadmap

- [ ] **Advanced Filtering**: Price range, availability, complexity
- [ ] **Recommendation Engine**: Machine learning-based suggestions
- [ ] **Image Search**: Visual similarity matching
- [ ] **Seasonal Recommendations**: Weather and occasion-based suggestions
- [ ] **User Preferences**: Personalized recommendation learning
- [ ] **Batch Operations**: Bulk similarity calculations
- [ ] **API Server**: REST API with FastAPI
- [ ] **Web Interface**: Interactive cocktail discovery UI

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

## 📜 License

This project is licensed under the MIT License.

## 🙏 Acknowledgments

- **Bar Assistant**: Source of cocktail data schema
- **pgvector**: Vector similarity search in PostgreSQL
- **OpenAI**: Embedding generation
- **SentenceTransformers**: Fallback embedding model
