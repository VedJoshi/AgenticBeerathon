# 🍸 Clanker That Recommends Alcohol - Production Ready API

## Overview

**Clanker That Recommends Alcohol** is now a production-ready API that returns structured JSON responses perfect for frontend integration. The bot analyzes movie data and provides personalized alcoholic beverage recommendations.

## 🔧 Production Enhancements Made

### 1. **Structured JSON Response Format**
- ✅ **Complete type safety** with Pydantic models
- ✅ **Consistent error handling** with structured error responses
- ✅ **Rich metadata** including processing times and API version
- ✅ **Both structured data AND formatted text** for flexibility

### 2. **Enhanced Error Handling**
- ✅ **Graceful AWS/AI service error handling**
- ✅ **Input validation** with clear error messages
- ✅ **Error codes** for programmatic handling
- ✅ **Detailed logging** for debugging

### 3. **Production API Features**
- ✅ **FastAPI with OpenAPI documentation**
- ✅ **Health monitoring endpoints**
- ✅ **Request timing middleware**
- ✅ **CORS support** for web frontends
- ✅ **Environment-based configuration**

### 4. **Improved AI Integration**
- ✅ **Enhanced prompts** for consistent output
- ✅ **Better parsing** with multiple regex patterns
- ✅ **Timeout handling** and retry logic
- ✅ **Comprehensive drink type support** (cocktails, wine, beer, spirits)

## 📊 What the Frontend Receives

### Success Response Structure

```json
{
  "success": true,
  "movie": {
    "title": "The Big Lebowski",
    "year": "1998",
    "genre": "Comedy, Crime",
    "runtime": "117 min",
    "rating": "8.1",
    "director": "Joel Coen, Ethan Coen",
    "plot": "Jeff 'The Dude' Lebowski, mistaken for a millionaire..."
  },
  "recommendation": {
    "name": "White Russian",
    "type": "cocktail",
    "base": "Vodka and coffee liqueur",
    "key_flavors": "Creamy, coffee, vanilla, cocoa",
    "glass": "Rocks glass or old-fashioned glass",
    "garnish": "None, or a sprinkle of ground coffee",
    "why_perfect": "The White Russian is the quintessential drink for The Big Lebowski...",
    "experience": "Sipping a White Russian while watching The Big Lebowski...",
    "recipe": "2 oz vodka, 1 oz Kahlua coffee liqueur, 1-2 oz cold milk or cream...",
    "alcohol_content": "Approx. 15-20% ABV",
    "difficulty": "Easy"
  },
  "formatted_text": "## 🎬 The Big Lebowski (1998)\\n**Comedy, Crime • 117 min • ⭐ 8.1/10**\\n...",
  "metadata": {
    "processing_time_seconds": 10.32,
    "model_used": "anthropic.claude-3-sonnet-20240229-v1:0",
    "api_version": "2.0.0",
    "timestamp": "2025-09-03T20:07:18.172244"
  }
}
```

### Error Response Structure

```json
{
  "success": false,
  "error": "Missing required movie data fields: Director",
  "error_code": "VALIDATION_ERROR",
  "details": {
    "missing_fields": ["Director"],
    "timestamp": "2025-09-03T20:07:18.172244"
  }
}
```

## 🔌 API Endpoints

### 1. `POST /recommend-drink/`
**Input:**
```json
{
  "movie_data": {
    "Title": "Casablanca",
    "Year": "1942",
    "Genre": "Drama, Romance, War",
    "Director": "Michael Curtiz",
    "Plot": "A cynical expatriate American cafe owner...",
    "Runtime": "102 min",
    "imdbRating": "8.5"
  }
}
```

**Output:** Complete `ClankerResponse` JSON (shown above)

### 2. `GET /health`
**Output:**
```json
{
  "status": "healthy",
  "service": "Clanker That Recommends Alcohol",
  "version": "2.0.0",
  "timestamp": "2025-09-03T20:07:18.172244"
}
```

### 3. `GET /`
**Output:** API information and available endpoints

## 🎯 Frontend Integration Guide

### 1. **Making Requests**
```javascript
const response = await fetch('http://localhost:8000/recommend-drink/', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    movie_data: {
      Title: "Casablanca",
      Year: "1942",
      Genre: "Drama, Romance, War",
      Director: "Michael Curtiz",
      // ... other OMDB fields
    }
  })
});

const result = await response.json();
```

### 2. **Handling Responses**
```javascript
if (result.success) {
  // Success - display recommendation
  const drink = result.recommendation;
  const movie = result.movie;
  
  displayDrink({
    name: drink.name,
    type: drink.type,
    recipe: drink.recipe,
    whyPerfect: drink.why_perfect,
    // ... use structured data
  });
  
  // OR use formatted markdown text
  displayMarkdown(result.formatted_text);
  
} else {
  // Error - show user-friendly message
  showError(result.error, result.error_code);
}
```

### 3. **TypeScript Types**
```typescript
interface ClankerResponse {
  success: true;
  movie: {
    title: string;
    year: string;
    genre: string;
    runtime?: string;
    rating?: string;
    director: string;
    plot?: string;
  };
  recommendation: {
    name: string;
    type: 'cocktail' | 'wine' | 'beer' | 'spirit';
    base: string;
    key_flavors: string;
    glass: string;
    garnish?: string;
    why_perfect: string;
    experience: string;
    recipe: string;
    alcohol_content?: string;
    difficulty?: string;
  };
  formatted_text?: string;
  metadata: {
    processing_time_seconds: number;
    model_used: string;
    api_version: string;
    timestamp: string;
  };
}

interface ErrorResponse {
  success: false;
  error: string;
  error_code: string;
  details?: Record<string, any>;
}
```

## 🚀 Deployment

### Docker
```bash
docker build -t clanker-api .
docker run -p 8000:8000 -e AWS_ACCESS_KEY_ID=xxx -e AWS_SECRET_ACCESS_KEY=xxx clanker-api
```

### Direct Python
```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export AWS_REGION=us-east-1
export AWS_ACCESS_KEY_ID=your_key
export AWS_SECRET_ACCESS_KEY=your_secret

# Run the server
python src/beer_clanker_bot/api.py
```

## 🔧 Configuration

Environment variables:
- `AWS_REGION` - AWS region (default: us-east-1)
- `AWS_ACCESS_KEY_ID` - AWS access key
- `AWS_SECRET_ACCESS_KEY` - AWS secret key
- `CLANKER_API_VERSION` - API version
- `CLANKER_ENVIRONMENT` - Environment (development/production)
- `CLANKER_DEBUG` - Enable debug mode
- `PORT` - Server port (default: 8000)

## 📝 Key Benefits for Frontend

1. **Predictable Structure**: Always know what fields will be present
2. **Error Handling**: Clear success/failure indication with detailed error info
3. **Flexibility**: Use structured data for custom UI or formatted text for quick display
4. **Rich Metadata**: Processing times, versions, timestamps for analytics
5. **Type Safety**: Full TypeScript support with provided interfaces
6. **Performance**: Optimized prompts and caching-ready responses

## 🎭 Example Outputs

The bot now intelligently recommends:
- **Cocktails** for classic films (French 75 for Casablanca)
- **Iconic drinks** from movies (White Russian for The Big Lebowski) 
- **Wine** for sophisticated dramas
- **Beer** for action movies
- **Spirits** for gritty crime films

Each recommendation includes complete recipe/purchasing information and explains the perfect pairing reasoning.

---

**The production-ready Clanker That Recommends Alcohol API is now ready for frontend integration!** 🍸🎬
