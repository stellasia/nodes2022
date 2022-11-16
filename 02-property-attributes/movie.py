from properties import Property
from nodes import Node


class Movie(Node):
    title = Property(is_required=True)
    released = Property()
