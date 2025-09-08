from fastapi import FastAPI, Request
from movie_cocktail_demo import MovieCocktailAgent

app = FastAPI()
agent = MovieCocktailAgent()


@app.post("/pairing")
async def get_pairing(request: Request):
    data = await request.json()
    movie = data.get("movie")
    # Use the agent's async method
    result = await agent.get_cocktail_for_movie(movie)
    return result
