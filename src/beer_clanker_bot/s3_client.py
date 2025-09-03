import boto3
import pandas as pd
import io
import os
from typing import Dict, List, Optional

class S3CocktailClient:
    def __init__(self, bucket_name: str, csv_key: str):
        self.s3 = boto3.client('s3', region_name=os.getenv('AWS_REGION', 'us-east-1'))
        self.bucket_name = bucket_name
        self.csv_key = csv_key
        self.cocktails_df = None
        self.load_cocktails()
    
    def load_cocktails(self):
        """Load cocktails from S3 CSV"""
        try:
            # Download CSV from S3
            response = self.s3.get_object(Bucket=self.bucket_name, Key=self.csv_key)
            csv_content = response['Body'].read().decode('utf-8')
            
            # Load into pandas DataFrame
            self.cocktails_df = pd.read_csv(io.StringIO(csv_content))
            print(f"✅ Loaded {len(self.cocktails_df)} cocktails from S3")
            
        except Exception as e:
            print(f"❌ Error loading cocktails from S3: {e}")
            self.cocktails_df = pd.DataFrame()  # Empty fallback
    
    def search_cocktail(self, name: str) -> Optional[Dict]:
        """Search for cocktail by name"""
        if self.cocktails_df.empty:
            return None
            
        # Case-insensitive search
        matches = self.cocktails_df[
            self.cocktails_df['name'].str.contains(name, case=False, na=False)
        ]
        
        if not matches.empty:
            cocktail = matches.iloc[0]  # Get first match
            return {
                'name': cocktail.get('name', ''),
                'description': cocktail.get('description', ''),
                'ingredients': cocktail.get('ingredients', ''),
                'flavor_profile': cocktail.get('flavor_profile', ''),
                'tags': cocktail.get('tags', ''),
                'glass': cocktail.get('glass', ''),
                'method': cocktail.get('method', ''),
                'instructions': cocktail.get('instructions', '')
            }
        return None
    
    def get_cocktail_context(self, limit: int = 10) -> str:
        """Get sample cocktails for AI context"""
        if self.cocktails_df.empty:
            return "No cocktails available."
            
        # Get random sample or first N cocktails
        sample = self.cocktails_df.head(limit) if len(self.cocktails_df) >= limit else self.cocktails_df
        
        context = "Available Cocktails:\n"
        for _, cocktail in sample.iterrows():
            context += f"- {cocktail.get('name', 'Unknown')}: {cocktail.get('description', 'No description')}\n"
            context += f"  Ingredients: {cocktail.get('ingredients', 'N/A')}\n"
            context += f"  Flavor: {cocktail.get('flavor_profile', 'N/A')}\n"
            context += f"  Glass: {cocktail.get('glass', 'N/A')}\n\n"
        
        return context
    
    def get_all_cocktail_names(self) -> List[str]:
        """Get list of all cocktail names for suggestions"""
        if self.cocktails_df.empty:
            return []
        return self.cocktails_df['name'].tolist()
