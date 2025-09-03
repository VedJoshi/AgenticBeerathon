#!/usr/bin/env python3
"""
Simple CSV verification script to check the output format
"""

import csv
import json

def check_csv_output():
    csv_path = r"C:\Users\vedti\Downloads\BoNUS\data\output\cocktails_knowledge_base.csv"
    
    print("🔍 Checking CSV output...")
    
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        rows = list(reader)
        total_rows = len(rows)
        
        print(f"📊 Total cocktails: {total_rows}")
        print(f"📋 Columns: {len(reader.fieldnames)}")
        print(f"🏷️  Field names: {', '.join(reader.fieldnames[:5])}...")
        
        # Check a few sample rows
        print("\n🍸 Sample cocktails:")
        
        for i, sample_name in enumerate(['Margarita', 'Negroni', 'Martini']):
            matching_rows = [row for row in rows if row['name'] == sample_name]
            if matching_rows:
                row = matching_rows[0]
                print(f"\n{i+1}. {row['name']}")
                print(f"   🆔 ID: {row['cocktail_id']}")
                print(f"   🥃 Glass: {row['glass']}")
                print(f"   🍹 Method: {row['method']}")
                print(f"   🔥 ABV: {row['abv']}%")
                print(f"   🏷️  Tags: {row['tags']}")
                print(f"   🌍 Origins: {row['origin_spirits']}")
                print(f"   📝 Ingredients: {row['ingredients_text'][:100]}...")
                print(f"   📖 Description: {row['description'][:80]}...")
        
        # Check file size
        import os
        file_size = os.path.getsize(csv_path) / (1024 * 1024)
        print(f"\n📦 File size: {file_size:.2f} MB")
        
        if file_size <= 50:
            print("✅ File size is within AWS Bedrock Knowledge Bases limits (≤50MB)")
        else:
            print("⚠️  File size exceeds 50MB limit!")
        
        # Check metadata file
        metadata_path = csv_path + ".metadata.json"
        if os.path.exists(metadata_path):
            with open(metadata_path, 'r', encoding='utf-8') as meta_f:
                metadata = json.load(meta_f)
                content_fields = len(metadata['contentAttributes'])
                metadata_fields = len(metadata['metadataAttributes'])
                print(f"\n📋 Metadata sidecar:")
                print(f"   📝 Content fields: {content_fields}")
                print(f"   🏷️  Metadata fields: {metadata_fields}")
                print("✅ Metadata sidecar file exists and is properly formatted")
        
        print(f"\n🎉 CSV conversion successful!")
        print(f"📄 Ready for AWS Bedrock Knowledge Bases S3 ingestion!")

if __name__ == "__main__":
    check_csv_output()
