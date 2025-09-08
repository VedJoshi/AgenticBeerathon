# Clanker That Recommends Alcohol

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.9+-blue.svg)
![API](https://img.shields.io/badge/API-FastAPI-green.svg)

A production-ready AI-powered movie-to-drink recommendation engine that suggests the perfect beverage (cocktail, wine, or beer) to enhance your movie-watching experience.

## Features

- 🎬 Movie input: Takes standardized movie data (OMDB API format)
- 🍸 Intelligent beverage pairing: Matches drinks to movie themes, mood, and setting
- 🍷 Diverse recommendations: Suggests cocktails, wines, beers, and spirits
- 🤖 AI-powered: Uses Claude AI for sophisticated, contextual recommendations
- 🔌 Multiple integration options: API, direct code integration, or demo mode

## Quick Start

```bash
# Clone the repository
git clone https://github.com/VedJoshi/clanker-recommends.git
cd clanker-recommends

# Install dependencies
pip install -r requirements.txt

# Set environment variables (or create .env file)
export AWS_REGION=us-east-1
export AWS_ACCESS_KEY_ID=your_access_key
export AWS_SECRET_ACCESS_KEY=your_secret_key

# Run the demo
python clanker_demo.py

# Or start the API server
python -m src.beer_clanker_bot.api
```

## API Usage

Once the server is running, you can interact with it:

```bash
# Example cURL request
curl -X POST http://localhost:8000/recommend-drink/ \
  -H "Content-Type: application/json" \
  -d '{
    "movie_data": {
      "Title": "Casablanca",
      "Year": "1942",
      "Genre": "Drama, Romance, War",
      "Director": "Michael Curtiz",
      "Plot": "A cynical expatriate American cafe owner struggles to decide whether or not to help his former lover and her fugitive husband escape the Nazis in French Morocco.",
      "Runtime": "102 min",
      "imdbRating": "8.5"
    }
  }'
```

Interactive API documentation is available at `http://localhost:8000/docs`

## Direct Integration

```python
from src.beer_clanker_bot.simplified_app import ClankerRecommender

# Initialize the recommender
recommender = ClankerRecommender()

# Example movie data
movie_data = {
    "Title": "The Godfather",
    "Year": "1972",
    "Genre": "Crime, Drama",
    "Director": "Francis Ford Coppola",
    "Plot": "The aging patriarch of an organized crime dynasty transfers control of his clandestine empire to his reluctant son.",
    "Runtime": "175 min",
    "imdbRating": "9.2"
}

# Get recommendation
result = recommender.process_movie_data(movie_data)
print(result)
```

## Deployment

### Local Deployment

```bash
python deploy.py --mode local
```

### Docker Deployment

```bash
python deploy.py --mode docker
```

## Architecture

```
├── src/
│   └── beer_clanker_bot/
│       ├── simplified_app.py    # Main application
│       ├── simplified_client.py # AI client
│       └── api.py              # FastAPI endpoints
├── clanker_demo.py            # Demo script
├── direct_example.py          # Direct usage example
├── deploy.py                  # Deployment utilities
├── Dockerfile                 # Docker configuration
├── requirements.txt           # Dependencies
└── README.md                  # Documentation
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
