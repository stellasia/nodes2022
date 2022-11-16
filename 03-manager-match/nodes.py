from properties import Property
from manager import NodeManager


class NodeBase(type):
    def __new__(mcs, name, bases, attrs):
        properties = {}
        for attr_name, attr in attrs.items():
            if isinstance(attr, Property):
                properties[attr_name] = attr
        attrs["_properties"] = properties
        kls = type.__new__(mcs, name, bases, attrs)
        return kls

    def __init__(cls, name, bases, attrs):
        # NEW
        cls.q = NodeManager(cls)
        super().__init__(name, bases, attrs)


class Node(metaclass=NodeBase):

    def __init__(self, /, **kwargs):
        self.cached_properties = {}
        for fn, prop in self._properties.items():
            val = kwargs.pop(fn, None)
            setattr(self, fn, val)

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
    def hydrate(cls, node):
        node_data = {
            k: node.get(k, None)
            for k in cls._properties
        }
        return cls(**node_data)
