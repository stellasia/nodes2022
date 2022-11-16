import enum

from utils import node_registry
from utils.db import connection


class Property:
    def __init__(self, /, is_required: bool = False):
        # NEW
        self.is_required = is_required

    def __set_name__(self, owner, name):
        self.name = name

    def __set__(self, instance, __value):
        if self.is_required and __value is None:
            raise ValueError(f"{self.name} is required")
        cache = instance.cached_properties
        cache[self.name] = self._validate(__value)

    def __get__(self, instance, owner):
        cache = instance.cached_properties
        return cache.get(self.name)

    def _validate(self, __value):
        return __value


class RelationshipDirection(enum.Enum):
    IN = "IN"
    OUT = "OUT"
    UNDIRECTED = "UNDIRECTED"


class RelationshipProperty(Property):
    def __init__(self,
                 relationship_type: str,
                 target_node_label: str,
                 relationship_direction: RelationshipDirection = RelationshipDirection.UNDIRECTED,
                 ):
        super().__init__()
        self.relationship_type = relationship_type
        self.target_node_label = target_node_label
        self.relationship_direction = relationship_direction

    def target_node_klass(self):
        return node_registry.get(self.target_node_label)

    def __get__(self, instance, owner):
        if (result := instance.cached_properties.get(self.name)) is not None:
            print(f"Using cached result for {self.name}")
            return result
        print(f"Fetching new result for {self.name}")
        result = self._fetch(instance)
        instance.cached_properties[self.name] = result
        return result

    def relationship_pattern(self):
        if self.relationship_type:
            rel = f"[:{self.relationship_type}]"
        else:
            rel = "[]"
        if self.relationship_direction == RelationshipDirection.IN:
            return f"<-{rel}-"
        if self.relationship_direction == RelationshipDirection.OUT:
            return f"-{rel}->"
        return f"-{rel}-"

    def target_node_pattern(self, alias=""):
        return f"({alias}:{self.target_node_label})"

    def _fetch(self, instance):
        query = f"""
        MATCH (start){self.relationship_pattern()}{self.target_node_pattern('node')}
        WHERE id(start) = {instance._id}
        RETURN node {{ .*, _id: id(node) }}
        """
        result_set = connection.cypher(query)
        target_node_class = self.target_node_klass()
        result = []
        for row in result_set:
            obj = target_node_class.hydrate(**row["node"])
            result.append(obj)
        return result
