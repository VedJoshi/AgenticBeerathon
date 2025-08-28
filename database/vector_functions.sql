-- Vector search functions for cocktail recommendations

-- Function to find similar cocktails based on flavor profile
CREATE OR REPLACE FUNCTION find_similar_cocktails_by_flavor(
    input_cocktail_id INTEGER,
    similarity_threshold DECIMAL DEFAULT 0.7,
    max_results INTEGER DEFAULT 10
)
RETURNS TABLE (
    cocktail_id INTEGER,
    cocktail_name VARCHAR(255),
    similarity_score DECIMAL,
    description TEXT,
    abv DECIMAL,
    method VARCHAR(255),
    glass VARCHAR(255)
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        c.id,
        c.name,
        (1 - (c.flavor_embedding <=> 
            (SELECT flavor_embedding FROM cocktails WHERE id = input_cocktail_id)
        ))::DECIMAL as similarity,
        c.description,
        c.abv,
        c.method,
        c.glass
    FROM cocktails c
    WHERE c.id != input_cocktail_id
        AND c.flavor_embedding IS NOT NULL
        AND (1 - (c.flavor_embedding <=> 
            (SELECT flavor_embedding FROM cocktails WHERE id = input_cocktail_id)
        )) >= similarity_threshold
    ORDER BY c.flavor_embedding <=> 
        (SELECT flavor_embedding FROM cocktails WHERE id = input_cocktail_id)
    LIMIT max_results;
END;
$$ LANGUAGE plpgsql;

-- Function to find cocktails with similar ingredients
CREATE OR REPLACE FUNCTION find_cocktails_by_ingredient_similarity(
    target_ingredients TEXT[],
    similarity_threshold DECIMAL DEFAULT 0.6,
    max_results INTEGER DEFAULT 15
)
RETURNS TABLE (
    cocktail_id INTEGER,
    cocktail_name VARCHAR(255),
    matching_ingredients INTEGER,
    total_ingredients INTEGER,
    match_percentage DECIMAL,
    description TEXT
) AS $$
BEGIN
    RETURN QUERY
    WITH cocktail_ingredient_matches AS (
        SELECT 
            c.id as cocktail_id,
            c.name as cocktail_name,
            c.description,
            COUNT(CASE WHEN i.name = ANY(target_ingredients) THEN 1 END) as matching_count,
            COUNT(*) as total_count
        FROM cocktails c
        JOIN cocktail_ingredients ci ON c.id = ci.cocktail_id
        JOIN ingredients i ON ci.ingredient_id = i.id
        GROUP BY c.id, c.name, c.description
    )
    SELECT 
        cim.cocktail_id,
        cim.cocktail_name,
        cim.matching_count::INTEGER,
        cim.total_count::INTEGER,
        (cim.matching_count::DECIMAL / cim.total_count::DECIMAL)::DECIMAL as match_pct,
        cim.description
    FROM cocktail_ingredient_matches cim
    WHERE (cim.matching_count::DECIMAL / cim.total_count::DECIMAL) >= similarity_threshold
        AND cim.matching_count > 0
    ORDER BY match_pct DESC, cim.matching_count DESC
    LIMIT max_results;
END;
$$ LANGUAGE plpgsql;

-- Function to search cocktails by flavor description
CREATE OR REPLACE FUNCTION search_cocktails_by_flavor_text(
    flavor_description TEXT,
    flavor_embedding vector(1536),
    max_results INTEGER DEFAULT 10,
    similarity_threshold DECIMAL DEFAULT 0.5
)
RETURNS TABLE (
    cocktail_id INTEGER,
    cocktail_name VARCHAR(255),
    similarity_score DECIMAL,
    description TEXT,
    tags TEXT[],
    method VARCHAR(255)
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        c.id,
        c.name,
        (1 - (c.description_embedding <=> flavor_embedding))::DECIMAL as similarity,
        c.description,
        c.tags,
        c.method
    FROM cocktails c
    WHERE c.description_embedding IS NOT NULL
        AND (1 - (c.description_embedding <=> flavor_embedding)) >= similarity_threshold
    ORDER BY c.description_embedding <=> flavor_embedding
    LIMIT max_results;
END;
$$ LANGUAGE plpgsql;

-- Function to find cocktails by method similarity
CREATE OR REPLACE FUNCTION find_cocktails_by_method_similarity(
    input_method VARCHAR(255),
    max_results INTEGER DEFAULT 8
)
RETURNS TABLE (
    cocktail_id INTEGER,
    cocktail_name VARCHAR(255),
    method VARCHAR(255),
    similarity_score DECIMAL,
    glass VARCHAR(255),
    abv DECIMAL
) AS $$
DECLARE
    method_embedding vector(1536);
BEGIN
    -- Get the method embedding for the input method
    SELECT c.method_embedding INTO method_embedding
    FROM cocktails c 
    WHERE c.method = input_method 
        AND c.method_embedding IS NOT NULL 
    LIMIT 1;
    
    IF method_embedding IS NULL THEN
        RAISE EXCEPTION 'No embedding found for method: %', input_method;
    END IF;
    
    RETURN QUERY
    SELECT 
        c.id,
        c.name,
        c.method,
        (1 - (c.method_embedding <=> method_embedding))::DECIMAL as similarity,
        c.glass,
        c.abv
    FROM cocktails c
    WHERE c.method_embedding IS NOT NULL
        AND c.method != input_method
    ORDER BY c.method_embedding <=> method_embedding
    LIMIT max_results;
END;
$$ LANGUAGE plpgsql;

-- Function to get ingredient recommendations based on cocktail
CREATE OR REPLACE FUNCTION get_ingredient_recommendations(
    cocktail_id INTEGER,
    max_results INTEGER DEFAULT 10
)
RETURNS TABLE (
    ingredient_id INTEGER,
    ingredient_name VARCHAR(255),
    category VARCHAR(255),
    similarity_score DECIMAL,
    description TEXT,
    strength DECIMAL
) AS $$
BEGIN
    RETURN QUERY
    WITH cocktail_ingredients_embedded AS (
        SELECT ARRAY_AGG(i.description_embedding) as embeddings
        FROM cocktail_ingredients ci
        JOIN ingredients i ON ci.ingredient_id = i.id
        WHERE ci.cocktail_id = get_ingredient_recommendations.cocktail_id
            AND i.description_embedding IS NOT NULL
    ),
    avg_embedding AS (
        SELECT 
            (SELECT AVG(embedding) FROM UNNEST(embeddings) as embedding) as avg_emb
        FROM cocktail_ingredients_embedded
    )
    SELECT 
        i.id,
        i.name,
        i.category,
        (1 - (i.description_embedding <=> ae.avg_emb))::DECIMAL as similarity,
        i.description,
        i.strength
    FROM ingredients i, avg_embedding ae
    WHERE i.description_embedding IS NOT NULL
        AND i.id NOT IN (
            SELECT ci.ingredient_id 
            FROM cocktail_ingredients ci 
            WHERE ci.cocktail_id = get_ingredient_recommendations.cocktail_id
        )
    ORDER BY i.description_embedding <=> ae.avg_emb
    LIMIT max_results;
END;
$$ LANGUAGE plpgsql;

-- Function to find cocktails suitable for specific dietary restrictions or preferences
CREATE OR REPLACE FUNCTION find_cocktails_by_preferences(
    preferred_strength_min DECIMAL DEFAULT 0,
    preferred_strength_max DECIMAL DEFAULT 50,
    excluded_categories TEXT[] DEFAULT '{}',
    required_tags TEXT[] DEFAULT '{}',
    max_results INTEGER DEFAULT 15
)
RETURNS TABLE (
    cocktail_id INTEGER,
    cocktail_name VARCHAR(255),
    abv DECIMAL,
    description TEXT,
    method VARCHAR(255),
    tags TEXT[]
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        c.id,
        c.name,
        c.abv,
        c.description,
        c.method,
        c.tags
    FROM cocktails c
    WHERE (c.abv IS NULL OR (c.abv >= preferred_strength_min AND c.abv <= preferred_strength_max))
        AND (array_length(required_tags, 1) IS NULL OR c.tags && required_tags)
        AND NOT EXISTS (
            SELECT 1 
            FROM cocktail_ingredients ci 
            JOIN ingredients i ON ci.ingredient_id = i.id
            WHERE ci.cocktail_id = c.id 
                AND i.category = ANY(excluded_categories)
        )
    ORDER BY c.abv ASC
    LIMIT max_results;
END;
$$ LANGUAGE plpgsql;
