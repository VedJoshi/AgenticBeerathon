from movie import MovieSearch


if __name__ == "__main__":
    movie_name = input("Enter movie name: ")
    year = input("Enter year (optional): ")
    movie = MovieSearch(
        title=movie_name, year=int(year) if year else None
    ).search_movie()
    if movie:
        print(movie)
    else:
        print("Movie not found.")
