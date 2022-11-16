from typing import Optional


class Movie:
    def __init__(self, title: str, released: Optional[int] = None):
        self.title = title
        self.released = released


def build_create_movie_query(movie: Movie):
    query = "CREATE (node:Movie) SET node.title=$title, node.released=$released"
    params = {
        "title": movie.title,
        "released": movie.released
    }
    return query, params
