# Cocktail Data Conversion for AWS Bedrock Knowledge Bases

## 📋 Summary

Successfully converted **557 cocktail JSON files** into a single CSV format suitable for AWS Bedrock Knowledge Bases S3 ingestion.

## 📄 Generated Files

### 1. `cocktails_knowledge_base.csv` (0.45 MB)
- **Format**: UTF-8 RFC4180 CSV with headers
- **Structure**: One row per cocktail (557 total)
- **Content**: Flattened ingredient descriptions for optimal searchability

### 2. `cocktails_knowledge_base.csv.metadata.json`
- **Purpose**: Metadata sidecar file for field mapping
- **Content Fields** (7): Searchable content for Knowledge Base queries
- **Metadata Fields** (9): Filterable attributes for precise retrieval

## 🔍 Data Structure

### Content Fields (Searchable)
- `cocktail_id`: Unique identifier
- `name`: Cocktail name
- `description`: Detailed cocktail description
- `instructions`: Preparation steps
- `ingredients_text`: Flattened ingredient descriptions with amounts and notes
- `garnish`: Garnish instructions
- `source`: Recipe source URL

### Metadata Fields (Filterable)
- `glass`: Glass type (e.g., "Margarita", "Lowball", "Cocktail")
- `method`: Preparation method (e.g., "Shake", "Build", "Stir")
- `abv`: Alcohol by volume percentage
- `tags`: Comma-separated tags (e.g., "IBA Cocktail", "Contemporary Classics")
- `origin_spirits`: Origin countries of main spirits
- `ingredient_count`: Number of ingredients
- `has_alcohol`: Boolean indicating alcoholic content
- `year`: Year of creation (if available)
- `created_at`: Creation timestamp

## 🚀 AWS Bedrock Knowledge Bases Setup

### 1. S3 Upload
```bash
# Upload both files to your S3 bucket
aws s3 cp cocktails_knowledge_base.csv s3://your-bucket/knowledge-base/
aws s3 cp cocktails_knowledge_base.csv.metadata.json s3://your-bucket/knowledge-base/
```

### 2. Knowledge Base Configuration
- **Data Source**: S3
- **File Format**: CSV with metadata sidecar
- **Chunking Strategy**: Default (recommended) or fixed token size
- **Content Fields**: Will be indexed for semantic search
- **Metadata Fields**: Available for filtering and attribution

### 3. Sample Queries
- "What cocktails use gin and lime juice?"
- "Find bitter cocktails that are stirred, not shaken"
- "Show me Mexican tequila cocktails with high ABV"
- "What are the ingredients and instructions for a Negroni?"

## ✅ Compliance

- ✅ **File Size**: 0.45 MB (well under 50 MB limit)
- ✅ **Format**: UTF-8 RFC4180 CSV (supported format)
- ✅ **Structure**: One document per cocktail row
- ✅ **Metadata**: Proper sidecar for content/metadata separation
- ✅ **Granularity**: Optimal for retrieval and citation

## 🔧 Script Features

The conversion script (`cocktail_json_to_csv.py`) includes:

- **Error Handling**: Robust processing of malformed JSON
- **Data Validation**: Ensures all required fields are present
- **Ingredient Flattening**: Converts complex ingredient objects to readable text
- **Origin Extraction**: Identifies spirit origins for geographical filtering
- **Size Monitoring**: Warns if file exceeds AWS limits
- **Logging**: Detailed processing information

## 📝 Notes

- **Ingredient Text**: Formatted as "Name (Amount Units) - Description" for readability
- **Tags**: Combined into comma-separated strings for easy filtering
- **Optional Ingredients**: Clearly marked in the ingredient text
- **ABV Calculation**: Preserved from original data for alcohol content filtering
- **Image References**: Not included in CSV (file-based assets not suitable for text search)

Ready for Knowledge Base ingestion! 🎉
