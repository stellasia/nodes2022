# NODES 2022

Accompanying code for my talk at the 
[NODES 2022](https://hopin.com/events/nodes-2022/registration) 
conference titled: "Building a Python/Neo4j OGM".

## Video

[![image](https://img.youtube.com/vi/DKziks5jQvc/maxresdefault.jpg)](https://youtu.be/DKziks5jQvc)

## Usage

Each folder can be seen as a new "branch", where features are
added incrementally.


    pip install -r requirements.txt
    export PYTHONPATH=.$PYTHONPATH

    pytest <dir>/tests.py


```bash
 pytest 00-movie-creation/tests.py
 pytest 01-node-class/tests.py 
 pytest 02-property-attributes/tests.py
 pytest 03-manager-match/tests.py 
 pytest 04-relationship-property-fetch-and-cache/tests.py 
 pytest 05-prefetch/tests.py 
```

## Content

- **00-movie-creation**: movie class and hard-coded CREATE statement
- **01-node-class**: Property and Node (w/ metaclass) => all subclasses of the `Node` class now have 
    a `_properties` attribute with a list of properties they accept
- **02-property-attributes**: define a Property as required (NB: skipped during the talk)
- **03-manager-match**: dynamically build MATCH clause, RETURN statement, object hydration from DB
- **04-relationship-property-fetch-and-cache**: define RelationshipProperty and ability to fetch the data
    when the field is accessed (ie when using `movie.actors` for instance)
- **05-prefetch**: ability to prefetch related object during the MATCH query thanks to Cypher map projection


## Map projection examples

```
MATCH (node:Movie {title: "Cloud Atlas"}) 
RETURN node { .* }

MATCH (node:Movie {title: "Cloud Atlas"}) 
RETURN node { .title, _id: id(node) }

MATCH (node:Movie {title: "Cloud Atlas"})
RETURN node {
     .title, 
     actors: [(node)<-[:ACTED_IN]-(person:Person) 
                 | person { .name }
            ]
}

MATCH (node:Movie {title: "Cloud Atlas"})
RETURN node {
     .title, 
     actors: [
        (node)<-[:ACTED_IN]-(person:Person) 
         | person { 
            .name, 
            directed: [
                (person)-[:DIRECTED]->(directed:Movie)
                | directed { .* }
            ] 
         }
     ]
}
```

## Full code

The code presented here is a simplified version extracted
from this project: [pentaquark](https://github.com/stellasia/pentaquark)
