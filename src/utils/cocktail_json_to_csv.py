#!/usr/bin/env python3
"""
Cocktail JSON to CSV Converter for AWS Bedrock Knowledge Bases

This script converts cocktail JSON files to a single CSV format suitable for 
AWS Bedrock Knowledge Bases S3 ingestion, with a metadata sidecar file.

Features:
- Processes all cocktail JSON files from the data directory
- Creates a single CSV with one row per cocktail
- Flattens ingredient data into readable text descriptions
- Generates metadata sidecar file for proper content/metadata field mapping
- Follows UTF-8 RFC4180 CSV format requirements
"""

import json
import csv
import os
from pathlib import Path
from typing import Dict, List, Any
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class CocktailCSVConverter:
    def __init__(self, data_dir: str, output_dir: str):
        """
        Initialize the converter.
        
        Args:
            data_dir: Path to the cocktails data directory
            output_dir: Path where CSV and metadata files will be saved
        """
        self.data_dir = Path(data_dir)
        self.output_dir = Path(output_dir)
        self.cocktails_dir = self.data_dir / "data" / "cocktails"
        
        # Ensure output directory exists
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # CSV field definitions
        self.content_fields = [
            'cocktail_id', 'name', 'description', 'instructions', 
            'ingredients_text', 'garnish', 'source'
        ]
        
        self.metadata_fields = [
            'glass', 'method', 'abv', 'tags', 'origin_spirits', 
            'ingredient_count', 'has_alcohol', 'year', 'created_at'
        ]
        
        self.all_fields = self.content_fields + self.metadata_fields

    def extract_ingredient_text(self, ingredients: List[Dict[str, Any]]) -> str:
        """
        Convert ingredient list to readable text description.
        
        Args:
            ingredients: List of ingredient dictionaries
            
        Returns:
            Formatted ingredient text description
        """
        if not ingredients:
            return ""
        
        ingredient_parts = []
        
        for ingredient in ingredients:
            name = ingredient.get('name', 'Unknown ingredient')
            amount = ingredient.get('amount', '')
            units = ingredient.get('units', '')
            note = ingredient.get('note', '')
            optional = ingredient.get('optional', False)
            description = ingredient.get('description', '')
            
            # Build ingredient line
            ingredient_line = name
            
            # Add amount and units
            if amount and units:
                if isinstance(amount, (int, float)):
                    ingredient_line += f" ({amount} {units})"
                else:
                    ingredient_line += f" ({amount} {units})"
            elif amount:
                ingredient_line += f" ({amount})"
            
            # Add optional indicator
            if optional:
                ingredient_line += " (optional)"
            
            # Add note if present
            if note:
                ingredient_line += f" - {note}"
            
            # Add description for context (first sentence only to keep it concise)
            if description:
                first_sentence = description.split('.')[0] + '.'
                if len(first_sentence) < 100:  # Only add if it's reasonably short
                    ingredient_line += f". {first_sentence}"
            
            ingredient_parts.append(ingredient_line)
        
        return "; ".join(ingredient_parts)

    def extract_origin_spirits(self, ingredients: List[Dict[str, Any]]) -> str:
        """Extract the origin countries/regions of main spirits."""
        origins = set()
        for ingredient in ingredients:
            if ingredient.get('category') in ['Spirits', 'Tequila', 'Whiskey', 'Rum', 'Gin', 'Vodka']:
                origin = ingredient.get('origin')
                if origin:
                    origins.add(origin)
        return ", ".join(sorted(origins))

    def process_cocktail_file(self, cocktail_path: Path) -> Dict[str, Any]:
        """
        Process a single cocktail JSON file.
        
        Args:
            cocktail_path: Path to the cocktail's data.json file
            
        Returns:
            Dictionary with processed cocktail data
        """
        try:
            with open(cocktail_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Extract ingredients text
            ingredients = data.get('ingredients', [])
            ingredients_text = self.extract_ingredient_text(ingredients)
            
            # Extract tags as comma-separated string
            tags = data.get('tags', [])
            tags_str = ", ".join(tags) if tags else ""
            
            # Count alcoholic ingredients
            alcoholic_ingredients = [ing for ing in ingredients if ing.get('strength', 0) > 0]
            has_alcohol = len(alcoholic_ingredients) > 0
            
            # Extract origin spirits
            origin_spirits = self.extract_origin_spirits(ingredients)
            
            # Build the row data
            row_data = {
                # Content fields (searchable)
                'cocktail_id': data.get('_id', ''),
                'name': data.get('name', ''),
                'description': data.get('description', ''),
                'instructions': data.get('instructions', ''),
                'ingredients_text': ingredients_text,
                'garnish': data.get('garnish', ''),
                'source': data.get('source', ''),
                
                # Metadata fields (filterable)
                'glass': data.get('glass', ''),
                'method': data.get('method', ''),
                'abv': data.get('abv', ''),
                'tags': tags_str,
                'origin_spirits': origin_spirits,
                'ingredient_count': len(ingredients),
                'has_alcohol': has_alcohol,
                'year': data.get('year', ''),
                'created_at': data.get('created_at', '')
            }
            
            return row_data
            
        except Exception as e:
            logger.error(f"Error processing {cocktail_path}: {e}")
            return None

    def create_metadata_sidecar(self, csv_filename: str):
        """
        Create the metadata sidecar JSON file for the CSV.
        
        Args:
            csv_filename: Name of the CSV file
        """
        metadata = {
            "metadataAttributes": {
                "glass": "string",
                "method": "string", 
                "abv": "number",
                "tags": "string_list",
                "origin_spirits": "string",
                "ingredient_count": "number",
                "has_alcohol": "boolean",
                "year": "string",
                "created_at": "string"
            },
            "contentAttributes": [
                "cocktail_id",
                "name", 
                "description",
                "instructions",
                "ingredients_text",
                "garnish",
                "source"
            ]
        }
        
        metadata_filename = f"{csv_filename}.metadata.json"
        metadata_path = self.output_dir / metadata_filename
        
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Created metadata sidecar: {metadata_path}")

    def convert_to_csv(self, output_filename: str = "cocktails.csv"):
        """
        Convert all cocktail JSON files to a single CSV.
        
        Args:
            output_filename: Name of the output CSV file
        """
        if not self.cocktails_dir.exists():
            raise FileNotFoundError(f"Cocktails directory not found: {self.cocktails_dir}")
        
        cocktail_data = []
        processed_count = 0
        error_count = 0
        
        # Process all cocktail directories
        for cocktail_dir in self.cocktails_dir.iterdir():
            if cocktail_dir.is_dir():
                data_file = cocktail_dir / "data.json"
                if data_file.exists():
                    row_data = self.process_cocktail_file(data_file)
                    if row_data:
                        cocktail_data.append(row_data)
                        processed_count += 1
                    else:
                        error_count += 1
                else:
                    logger.warning(f"No data.json found in {cocktail_dir}")
        
        if not cocktail_data:
            raise ValueError("No cocktail data found to convert")
        
        # Write CSV file
        csv_path = self.output_dir / output_filename
        with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=self.all_fields)
            writer.writeheader()
            writer.writerows(cocktail_data)
        
        # Create metadata sidecar
        self.create_metadata_sidecar(output_filename)
        
        # Log results
        file_size_mb = csv_path.stat().st_size / (1024 * 1024)
        logger.info(f"Conversion completed:")
        logger.info(f"  - Processed: {processed_count} cocktails")
        logger.info(f"  - Errors: {error_count}")
        logger.info(f"  - Output CSV: {csv_path}")
        logger.info(f"  - File size: {file_size_mb:.2f} MB")
        
        if file_size_mb > 50:
            logger.warning("WARNING: File size exceeds 50MB limit for Bedrock Knowledge Bases!")
        
        return csv_path


def main():
    """Main function to run the conversion."""
    # Configuration
    data_dir = r"C:\Users\vedti\Downloads\BoNUS\data\cocktails"
    output_dir = r"C:\Users\vedti\Downloads\BoNUS\data\output"
    
    try:
        # Create converter and run conversion
        converter = CocktailCSVConverter(data_dir, output_dir)
        csv_path = converter.convert_to_csv("cocktails_knowledge_base.csv")
        
        print(f"\n✅ Conversion successful!")
        print(f"📄 CSV file: {csv_path}")
        print(f"📋 Metadata sidecar: {csv_path}.metadata.json")
        print(f"\n🚀 Files are ready for AWS Bedrock Knowledge Bases S3 ingestion!")
        
    except Exception as e:
        logger.error(f"Conversion failed: {e}")
        raise


if __name__ == "__main__":
    main()
