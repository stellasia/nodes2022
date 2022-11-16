from properties import Property


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
    def _get_params_from_kwargs(cls, **kwargs):
        params = {}
        for prop_name, prop in cls._properties.items():
            params[prop_name] = kwargs.get(prop_name, None)
        for k in kwargs:
            if k not in cls._properties:
                raise AttributeError(f"'{k}' is not a valid property for model {cls}")
        return params

    @classmethod
    def build_create_query(cls, **params):
        node_alias = "node"
        label = cls.__name__
        query = f"CREATE ({node_alias}:{label}) "

        set_query = [
            f"{node_alias}.{k}=${k}"
            for k in cls._properties
        ]
        set_query = ", ".join(set_query)
        if set_query:
            set_query = "SET " + set_query

        params = cls._get_params_from_kwargs(**params)

        query = query + set_query
        return query, params
