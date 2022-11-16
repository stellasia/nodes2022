from properties import Property, RelationshipProperty
from manager import NodeManager
from utils import node_registry


class NodeBase(type):
    def __new__(mcs, name, bases, attrs):
        properties = {
            "_id": Property(),
        }
        relationships = {}
        for attr_name, attr in attrs.items():
            if isinstance(attr, RelationshipProperty):
                relationships[attr_name] = attr
                continue
            if isinstance(attr, Property):
                properties[attr_name] = attr
        attrs["_properties"] = properties
        attrs["_relationships"] = relationships
        kls = type.__new__(mcs, name, bases, attrs)
        node_registry[name] = kls
        return kls

    def __init__(cls, name, bases, attrs):
        cls.q = NodeManager(cls)
        super().__init__(name, bases, attrs)


class Node(metaclass=NodeBase):

    def __init__(self, /, **kwargs):
        self.cached_properties = {}
        for fn, prop in self._properties.items():
            val = kwargs.pop(fn, None)
            setattr(self, fn, val)
        # for fn, prop in self._relationships.items():
        #     val = kwargs.pop(fn, None)
        #     self.cached_properties[fn] = val

    @classmethod
    def labels(cls) -> list[str]:
        return [cls.__name__, ]

    def prop_dict(self):
        return {
            pn: getattr(self, pn, None)
            for pn in self._properties
        }

    def __str__(self):
        return f"<{self.__class__.__name__}: {self.prop_dict()}>"

    def __repr__(self):
        return str(self)

    @classmethod
    def hydrate(cls, **params):
        node_data = {
            k: params.get(k, None)
            for k in cls._properties
        }
        # for rel_name, rel_prop in cls._relationships.items():
        #     targets = []
        #     if rel_name not in params:
        #         continue
        #     target_data = params[rel_name]
        #     for data in target_data:
        #         targets.append(
        #             rel_prop.target_node_klass().hydrate(**data)
        #         )
        #     node_data[rel_name] = targets
        return cls(**node_data)
