import pytest
from movie import Movie


def test_movie_object():
    m = Movie(title="The Matrix")
    assert m.title == "The Matrix"
    assert m.released is None


@pytest.fixture
def movie_data():
    yield {"title": "NODES", "released": 2022}


def test_create_query(movie_data):
    q, p = Movie.build_create_query(**movie_data)
    assert q == "CREATE (node:Movie) SET node.title=$title, node.released=$released"
    assert p == {"title": movie_data["title"], "released": movie_data["released"]}


def test_create_query_raises_if_unknown_property(movie_data):
    with pytest.raises(AttributeError):
        Movie.build_create_query(**movie_data, non_existing="toto")


def test_create_movie_raises_if_required_property_is_absent():
    with pytest.raises(ValueError):
        # title is required but not provided here
        Movie(released=2022)
