from properties import Property, RelationshipProperty, RelationshipDirection
from nodes import Node


class Movie(Node):
    title = Property(is_required=True)
    released = Property()
    actors = RelationshipProperty(relationship_type="ACTED_IN", target_node_label="Person")


class Person(Node):
    name = Property(is_required=True)
    directed = RelationshipProperty("DIRECTED", "Movie", relationship_direction=RelationshipDirection.OUT)
