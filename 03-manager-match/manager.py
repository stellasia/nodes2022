# NEW
from utils.db import connection

LABEL_TYPE_MARKER = ":"


class NodeManager:
    def __init__(self, node_model):
        self.model = node_model

    def create_query(self, **kwargs) -> tuple[str, dict]:
        node_alias = "node"
        set_statement, params = self._set_statement(node_alias, **kwargs)
        query = f"{self._create_statement(node_alias)} {set_statement}"
        return query, params

    def _node_repr(self, node_alias=None):
        labels = self._labels_statement()
        return f"({node_alias if node_alias else ''}{labels})"

    def _labels_statement(self) -> str:
        return LABEL_TYPE_MARKER + LABEL_TYPE_MARKER.join(self.model.labels())

    def _create_statement(self, node_alias) -> str:
        return f"CREATE {self._node_repr(node_alias)}"

    def _get_params_from_kwargs(self, **kwargs):
        params = {}
        for prop_name, prop in self.model._properties.items():
            if prop_name in kwargs:
                params[prop_name] = kwargs[prop_name]
        for k in kwargs:
            if k not in self.model._properties:
                raise AttributeError(f"'{k}' is not a valid property for model {self.model}")
        return params

    def _set_statement(self, node_alias, **kwargs) -> tuple[str, dict]:
        set_query = [
            f"{node_alias}.{k}=${k}"
            for k in self.model._properties
        ]
        set_query = ", ".join(set_query)
        if set_query:
            set_query = "SET " + set_query
        params = self._get_params_from_kwargs(**kwargs)
        return set_query, params

    def create(self, **kwargs):
        connection.cypher(*self.create_query(**kwargs))
        return True

    # NEW
    def match_query(self, filters: dict, node_alias: str = "node") -> tuple[str, dict]:
        match_statement = self._match_statement(node_alias)
        where_query, params = self._where_statement(node_alias, **filters)
        return_query = self._return_statement(node_alias)
        match_statement += f" {where_query} {return_query}"
        return match_statement, params

    def _match_statement(self, node_alias) -> str:
        return f"MATCH {self._node_repr(node_alias)}"

    def _where_statement(self, node_alias, **filters):
        where_query = [
            f"{node_alias}.{k}=${k}"
            for k in filters
        ]
        where_query = " AND ".join(where_query)
        if where_query:
            where_query = "WHERE " + where_query
        params = self._get_params_from_kwargs(**filters)
        return where_query, params

    def _return_statement(self, node_alias):
        return f"RETURN {node_alias}"
        # return f"RETURN {node_alias} {{ .* }}"

    def match(self, filters):
        node_alias = "node"
        query, params = self.match_query(filters, node_alias=node_alias)
        res = connection.cypher(query, params=params)
        if not res:
            # if res is empty, not found
            return None
        # assume single match here
        node = res[0][node_alias]
        return self.model.hydrate(node)
