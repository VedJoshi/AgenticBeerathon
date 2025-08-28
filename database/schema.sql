-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Drop existing tables if they exist (for development)
DROP TABLE IF EXISTS cocktail_ingredients CASCADE;
DROP TABLE IF EXISTS cocktails CASCADE;
DROP TABLE IF EXISTS ingredients CASCADE;

-- Ingredients table with vector embeddings
CREATE TABLE ingredients (
    id SERIAL PRIMARY KEY,
    _id VARCHAR(255) UNIQUE NOT NULL,
    _parent_id VARCHAR(255),
    name VARCHAR(255) NOT NULL,
    strength DECIMAL(5,2),
    description TEXT,
    origin VARCHAR(255),
    color VARCHAR(255),
    category VARCHAR(255),
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    images JSONB,
    ingredient_parts JSONB,
    prices JSONB,
    calculator_id VARCHAR(255),
    sugar_g_per_ml DECIMAL(10,4),
    acidity DECIMAL(10,4),
    distillery VARCHAR(255),
    units VARCHAR(50),
    -- Vector embeddings for semantic search
    description_embedding vector(1536), -- OpenAI embedding dimension
    flavor_profile_embedding vector(1536), -- For flavor characteristics
    category_embedding vector(1536), -- For category-based similarity
    created_at_db TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at_db TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Cocktails table with vector embeddings
CREATE TABLE cocktails (
    id SERIAL PRIMARY KEY,
    _id VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    instructions TEXT,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    description TEXT,
    source VARCHAR(500),
    garnish VARCHAR(255),
    abv DECIMAL(5,2),
    tags TEXT[],
    glass VARCHAR(255),
    method VARCHAR(255),
    utensils TEXT[],
    images JSONB,
    parent_cocktail_id VARCHAR(255),
    year INTEGER,
    -- Vector embeddings for semantic search
    description_embedding vector(1536), -- Full description embedding
    flavor_embedding vector(1536), -- Combined flavor profile from ingredients
    method_embedding vector(1536), -- Preparation method embedding
    ingredient_summary_embedding vector(1536), -- Summary of all ingredients
    tags_embedding vector(1536), -- Tags-based embedding
    created_at_db TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at_db TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Junction table for cocktail-ingredient relationships with amounts
CREATE TABLE cocktail_ingredients (
    id SERIAL PRIMARY KEY,
    cocktail_id INTEGER REFERENCES cocktails(id) ON DELETE CASCADE,
    ingredient_id INTEGER REFERENCES ingredients(id) ON DELETE CASCADE,
    amount DECIMAL(10,4),
    units VARCHAR(50),
    optional BOOLEAN DEFAULT FALSE,
    amount_max DECIMAL(10,4),
    note TEXT,
    sort_order INTEGER,
    is_specified BOOLEAN DEFAULT FALSE,
    substitutes JSONB,
    created_at_db TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(cocktail_id, ingredient_id, sort_order)
);

-- Indexes for vector similarity search
CREATE INDEX ON ingredients USING ivfflat (description_embedding vector_cosine_ops) WITH (lists = 100);
CREATE INDEX ON ingredients USING ivfflat (flavor_profile_embedding vector_cosine_ops) WITH (lists = 100);
CREATE INDEX ON ingredients USING ivfflat (category_embedding vector_cosine_ops) WITH (lists = 100);

CREATE INDEX ON cocktails USING ivfflat (description_embedding vector_cosine_ops) WITH (lists = 100);
CREATE INDEX ON cocktails USING ivfflat (flavor_embedding vector_cosine_ops) WITH (lists = 100);
CREATE INDEX ON cocktails USING ivfflat (method_embedding vector_cosine_ops) WITH (lists = 100);
CREATE INDEX ON cocktails USING ivfflat (ingredient_summary_embedding vector_cosine_ops) WITH (lists = 100);
CREATE INDEX ON cocktails USING ivfflat (tags_embedding vector_cosine_ops) WITH (lists = 100);

-- Traditional indexes for faster queries
CREATE INDEX idx_ingredients_name ON ingredients(name);
CREATE INDEX idx_ingredients_category ON ingredients(category);
CREATE INDEX idx_ingredients_origin ON ingredients(origin);
CREATE INDEX idx_ingredients_strength ON ingredients(strength);

CREATE INDEX idx_cocktails_name ON cocktails(name);
CREATE INDEX idx_cocktails_method ON cocktails(method);
CREATE INDEX idx_cocktails_glass ON cocktails(glass);
CREATE INDEX idx_cocktails_abv ON cocktails(abv);
CREATE INDEX idx_cocktails_tags ON cocktails USING GIN(tags);

CREATE INDEX idx_cocktail_ingredients_cocktail_id ON cocktail_ingredients(cocktail_id);
CREATE INDEX idx_cocktail_ingredients_ingredient_id ON cocktail_ingredients(ingredient_id);

-- Update timestamp trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at_db = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for automatic timestamp updates
CREATE TRIGGER update_ingredients_updated_at BEFORE UPDATE ON ingredients
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_cocktails_updated_at BEFORE UPDATE ON cocktails
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_cocktail_ingredients_updated_at BEFORE UPDATE ON cocktail_ingredients
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
