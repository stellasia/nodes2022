import pytest
from movie import Movie
from utils.db import connection


def test_movie_object():
    m = Movie(title="The Matrix")
    assert m.title == "The Matrix"
    assert m.released is None


@pytest.fixture
def movie_data():
    yield {"title": "NODES", "released": 2022}


def test_create_query(movie_data):
    q, p = Movie.q.create_query(**movie_data)
    assert q == "CREATE (node:Movie) SET node.title=$title, node.released=$released"
    assert p == {"title": movie_data["title"], "released": movie_data["released"]}


def test_create_query_raises_if_unknown_property(movie_data):
    with pytest.raises(AttributeError):
        Movie.q.create_query(**movie_data, non_existing="toto")


def test_create_movie_raises_if_required_property_is_absent():
    with pytest.raises(ValueError):
        # title is required but not provided here
        Movie(released=2022)


def test_match_query():
    query, params = Movie.q.match_query(filters={"title": "NODES"})
    assert query == "MATCH (node:Movie) WHERE node.title=$title RETURN node { .*, _id: id(node) }"
    assert params == {"title": "NODES"}


def test_match_query_unknown_property():
    with pytest.raises(AttributeError):
        Movie.q.match_query(filters={"non_existing": "NODES"})


def test_match():
    movie = Movie.q.match(filters={"title": "The Matrix"})
    assert isinstance(movie, Movie)
    assert movie.title == "The Matrix"
    assert movie.released == 1999
    assert movie._id is not None


def test_match_not_found():
    movie = Movie.q.match(filters={"title": "The Matrix 2"})
    assert movie is None


def test_fetch_related_objects():
    with connection.transaction() as t:
        movie = Movie.q.match(filters={"title": "The Matrix"})  # one query
        actors = movie.actors  # another query
        assert len(actors) == 5
        assert sorted([p.name for p in actors]) == \
               ['Carrie-Anne Moss',
                'Emil Eifrem',
                'Hugo Weaving',
                'Keanu Reeves',
                'Laurence Fishburne']
        assert t.number_of_queries == 2

        assert len(movie.actors) == 5
        assert t.number_of_queries == 2


def test_prefetch_related_objects():
    with connection.transaction() as t:
        movie = Movie.q.match(filters={"title": "The Matrix"}, return_fields=["title", "actors"])  # one query
        actors = movie.actors   # use cache result
        assert len(actors) == 5
        assert sorted([p.name for p in actors]) == \
               ['Carrie-Anne Moss',
                'Emil Eifrem',
                'Hugo Weaving',
                'Keanu Reeves',
                'Laurence Fishburne']
        assert t.number_of_queries == 1

        assert len(movie.actors) == 5
        assert t.number_of_queries == 1
