import pytest
from movie import build_create_movie_query, Movie


def test_movie_object():
    m = Movie(title="The Matrix")
    assert m.title == "The Matrix"
    assert m.released is None


@pytest.fixture
def movie():
    yield Movie(title="NODES", released=2022)


def test_movie_create_query(movie):
    q, p = build_create_movie_query(movie)
    assert q == "CREATE (node:Movie) SET node.title=$title, node.released=$released"
    assert p == {"title": movie.title, "released": movie.released}
