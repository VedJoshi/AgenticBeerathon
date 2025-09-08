# Clanker That Recommends Alcohol 🍸🎬

A **production-ready API** for generating personalized alcoholic beverage recommendations (cocktails, wines, and beers) based on movie data. Now with structured JSON responses perfect for frontend integration!

## ✨ New Production Features

- 🎯 **Structured JSON responses** with complete type safety
- 🛡️ **Robust error handling** and validation
- 📊 **Rich metadata** including processing times and API versioning
- 🔄 **Health monitoring** endpoints for production deployment
- 📚 **Interactive API documentation** with OpenAPI/Swagger
- 🎨 **Both structured data AND formatted markdown** for flexible frontend display

## Overview

This application takes movie data (in JSON format from OMDB API) as input, processes it through an AI model (Claude), and returns a tailored beverage recommendation that matches the movie's themes, mood, and setting.

**The bot intelligently recommends:**
- 🍸 Classic and creative **cocktails** 
- 🍷 Fine **wines** (red, white, sparkling)
- 🍺 Craft **beers** and specialty brews
- 🥃 Premium **spirits** and liqueurs

## Setup

1. **Install Dependencies**

```bash
pip install -r requirements.txt
```

2. **Set Environment Variables**

Create a `.env` file with the following:

```
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
```

## Usage

### Option 1: Use the API

Start the API server:

```bash
python -m src.beer_clanker_bot.api
```

Send a POST request to `/recommend-drink/` with the OMDB movie data:

```bash
curl -X POST http://localhost:8000/recommend-drink/ \
  -H "Content-Type: application/json" \
  -d '{"movie_data": {"Title": "Casablanca", "Year": "1942", ...}}'
```

Visit `http://localhost:8000/docs` for interactive API documentation.

### Option 2: Run the Demo Script

```bash
python clanker_demo.py
```

### Option 3: Use the Python Module Directly

```python
from src.beer_clanker_bot.simplified_app import ClankerRecommender

# Initialize the app
app = ClankerRecommender()

# Process movie data (either as dict or JSON string)
movie_data = {"Title": "Casablanca", "Year": "1942", ...}
result = app.process_movie_data(movie_data)
print(result)
```

## Input Format

The application expects movie data in the following format (from OMDB API):

```json
{
  "Title": "Casablanca",
  "Year": "1942",
  "Rated": "PG",
  "Runtime": "102 min",
  "Genre": "Drama, Romance, War",
  "Director": "Michael Curtiz",
  "Plot": "A cynical expatriate American cafe owner struggles to decide whether or not to help his former lover and her fugitive husband escape the Nazis in French Morocco.",
  "imdbRating": "8.5"
}
```

Note: Only the fields shown above are required; other fields will be ignored.

## 📊 What the Frontend Receives

### ✅ Success Response
```json
{
  "success": true,
  "movie": {
    "title": "The Big Lebowski",
    "year": "1998",
    "genre": "Comedy, Crime",
    "runtime": "117 min", 
    "rating": "8.1",
    "director": "Joel Coen, Ethan Coen"
  },
  "recommendation": {
    "name": "White Russian",
    "type": "cocktail",
    "base": "Vodka and coffee liqueur",
    "key_flavors": "Creamy, coffee, vanilla, cocoa",
    "glass": "Rocks glass",
    "recipe": "2 oz vodka, 1 oz Kahlua, 1-2 oz cream...",
    "why_perfect": "The White Russian is the quintessential drink...",
    "experience": "Sipping on a White Russian while watching...",
    "alcohol_content": "Approx. 15-20% ABV",
    "difficulty": "Easy"
  },
  "formatted_text": "## 🎬 The Big Lebowski (1998)\\n**Comedy, Crime • 117 min...",
  "metadata": {
    "processing_time_seconds": 10.32,
    "api_version": "2.0.0",
    "timestamp": "2025-09-03T20:07:18.172244"
  }
}
```

### ❌ Error Response
```json
{
  "success": false,
  "error": "Missing required movie data fields: Director",
  "error_code": "VALIDATION_ERROR",
  "details": {
    "missing_fields": ["Director"]
  }
}
```

## Deployment

### Docker

```bash
docker build -t clanker-api .
docker run -p 8000:8000 -e AWS_ACCESS_KEY_ID=your_key -e AWS_SECRET_ACCESS_KEY=your_secret clanker-api
```

### AWS Lambda

The API can be deployed as a Lambda function with API Gateway integration. See the `infrastructure/` directory for CloudFormation templates.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
