from typing import Literal, Optional
from pydantic import BaseModel
import http
import requests
import os
from dotenv import load_dotenv


class Rating(BaseModel):
    Source: str
    Value: str


class Movie(BaseModel):
    title: str
    year: str
    rated: str
    released: str
    runtime: str
    genre: str
    director: str
    writer: str
    actors: str
    plot: str
    language: str
    country: str
    awards: str
    poster: str
    ratings: list[Rating]
    metascore: str
    imdb_rating: str
    imdb_votes: str
    imdb_id: str
    type: str
    dvd: str
    box_office: str
    production: str
    website: str
    response: str

    def __str__(self) -> str:
        return (
            f"Title: {self.title}\n"
            f"Year: {self.year}\n"
            f"Rated: {self.rated}\n"
            f"Released: {self.released}\n"
            f"Runtime: {self.runtime}\n"
            f"Genre: {self.genre}\n"
            f"Director: {self.director}\n"
            f"Writer: {self.writer}\n"
            f"Actors: {self.actors}\n"
            f"Plot: {self.plot}\n"
            f"Language: {self.language}\n"
            f"Country: {self.country}\n"
            f"Awards: {self.awards}\n"
            f"Poster: {self.poster}\n"
            f"Ratings: {', '.join([f'{r.Source}: {r.Value}' for r in self.ratings])}\n"
            f"Metascore: {self.metascore}\n"
            f"IMDB Rating: {self.imdb_rating}\n"
            f"IMDB Votes: {self.imdb_votes}\n"
            f"IMDB ID: {self.imdb_id}\n"
            f"Type: {self.type}\n"
            f"DVD: {self.dvd}\n"
            f"Box Office: {self.box_office}\n"
            f"Production: {self.production}\n"
            f"Website: {self.website}\n"
            f"Response: {self.response}"
        )


class MovieSearch:
    title: str
    type: Optional[Literal["movie", "series", "episode"]] = "movie"
    year: Optional[int] = None
    plot: Optional[Literal["short", "full"]] = "full"

    def __init__(
        self,
        title: str,
        year: Optional[int] = None,
    ) -> None:
        self.title = title
        self.year = year

    def __get_search_url(self, api_key: str) -> str:
        base_url = "http://www.omdbapi.com/"

        return "%s?t=%s&type=%s&y=%s&plot=%s&apikey=%s" % (
            base_url,
            self.title,
            self.type,
            self.year if self.year else "",
            self.plot,
            api_key,
        )

    def search_movie(self) -> Optional[Movie]:
        load_dotenv()
        API_KEY = os.getenv("OMDB_API_KEY")
        if not API_KEY:
            raise ValueError("OMDB_API_KEY not found in environment variables.")

        url = self.__get_search_url(API_KEY)

        print("Searching for movie...")
        response = requests.get(url, timeout=10)
        if response.status_code == http.HTTPStatus.OK:
            data = response.json()
            # Map API fields to Movie fields
            ratings = [Rating(**r) for r in data.get("Ratings", [])]
            movie = Movie(
                title=data.get("Title", ""),
                year=data.get("Year", ""),
                rated=data.get("Rated", ""),
                released=data.get("Released", ""),
                runtime=data.get("Runtime", ""),
                genre=data.get("Genre", ""),
                director=data.get("Director", ""),
                writer=data.get("Writer", ""),
                actors=data.get("Actors", ""),
                plot=data.get("Plot", ""),
                language=data.get("Language", ""),
                country=data.get("Country", ""),
                awards=data.get("Awards", ""),
                poster=data.get("Poster", ""),
                ratings=ratings,
                metascore=data.get("Metascore", ""),
                imdb_rating=data.get("imdbRating", ""),
                imdb_votes=data.get("imdbVotes", ""),
                imdb_id=data.get("imdbID", ""),
                type=data.get("Type", ""),
                dvd=data.get("DVD", ""),
                box_office=data.get("BoxOffice", ""),
                production=data.get("Production", ""),
                website=data.get("Website", ""),
                response=data.get("Response", ""),
            )
            return movie
        else:
            print("Error fetching data from API.")
