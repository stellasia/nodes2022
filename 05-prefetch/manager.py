from typing import Optional, Type
from utils.db import connection

LABEL_TYPE_MARKER = ":"


class NodeManager:
    def __init__(self, node_model: Type["Node"]):
        self.model = node_model

    def create_query(self, **kwargs) -> tuple[str, dict]:
        node_alias = "node"
        set_statement, params = self._set_statement(node_alias, **kwargs)
        query = f"{self._create_statement(node_alias)} {set_statement}"
        return query, params

    def _node_repr(self, node_alias: Optional[str] = None) -> str:
        labels = self._labels_statement()
        return f"({node_alias if node_alias else ''}{labels})"

    def _labels_statement(self) -> str:
        return LABEL_TYPE_MARKER + LABEL_TYPE_MARKER.join(self.model.labels())

    def _create_statement(self, node_alias) -> str:
        return f"CREATE {self._node_repr(node_alias)}"

    def _get_params_from_kwargs(self, **kwargs) -> dict:
        params = {}
        for k, v in kwargs.items():
            if k not in self.model._properties:
                raise AttributeError(f"'{k}' is not a valid property for model {self.model}")
            params[k] = v
        return params

    def _set_statement(self, node_alias, **kwargs) -> tuple[str, dict]:
        set_query = [
            f"{node_alias}.{k}=${k}"
            for k in self.model._properties
            if not k.startswith("_")
        ]
        set_query = ", ".join(set_query)
        if set_query:
            set_query = "SET " + set_query
        params = self._get_params_from_kwargs(**kwargs)
        return set_query, params

    def create(self, **kwargs) -> bool:
        connection.cypher(*self.create_query(**kwargs))
        return True

    def match_query(self,
                    filters: dict, node_alias: str = "node", return_fields: Optional[list[str]] = None
                    ) -> tuple[str, dict]:
        match_statement = self._match_statement(node_alias)
        where_query, params = self._where_statement(node_alias, **filters)
        return_query = self._return_statement(node_alias, return_fields=return_fields)
        match_statement += f" {where_query} {return_query}"
        return match_statement, params

    def _match_statement(self, node_alias: str) -> str:
        return f"MATCH {self._node_repr(node_alias)}"

    def _where_statement(self, node_alias: str, **filters) -> tuple[str, dict]:
        where_query = [
            f"{node_alias}.{k}=${k}"
            for k in filters
        ]
        where_query = " AND ".join(where_query)
        if where_query:
            where_query = "WHERE " + where_query
        params = self._get_params_from_kwargs(**filters)
        return where_query, params

    def _return_statement(self, node_alias: str, return_fields: Optional[list[str]] = None) -> str:
        builder = ReturnQueryBuilder(node_alias=node_alias, model=self.model, return_fields=return_fields)
        return builder.build()

    def match(self, filters, return_fields: Optional[list[str]] = None) -> Optional["Node"]:
        node_alias = "node"
        query, params = self.match_query(filters, node_alias=node_alias, return_fields=return_fields)
        res = connection.cypher(query, params=params)
        if not res:
            # not found
            return None
        # assume single match here
        node = res[0][node_alias]
        return self.model.hydrate(**node)


class ReturnQueryBuilder:
    def __init__(self, node_alias: str, model: Type["Node"], return_fields: Optional[list[str]] = None):
        self.node_alias = node_alias
        self.model = model
        self.fields = return_fields or []

    def build(self):
        return f"RETURN {self.node_alias} {{ .*, _id: id({self.node_alias}) }}"

    # def build(self):
    #     return f"RETURN {self.node_alias} {{ {self._query_parts()} }}"
    #
    # def _query_parts(self):
    #     node_alias = self.node_alias or "node"
    #     return_query_parts = []
    #     for field_name in self.fields:
    #         if field_name == "":
    #             return_query_parts.append(".*")
    #             continue
    #         prop = self.model._properties.get(field_name, None)
    #         if prop is not None:
    #             return_query_parts.append(f".{field_name}")
    #             continue
    #         rel = self.model._relationships.get(field_name, None)
    #         if rel is None:
    #             raise ValueError(f"cannot return {field_name} which is not a valid property of {self.model}")
    #         # builder = ReturnQueryBuilder(node_alias=field_name, model=rel.target_node_klass(), fields=field.fields)
    #         return_query_parts.append(
    #             f"{field_name}: "
    #             f"[({node_alias}) {rel.relationship_pattern()} {rel.target_node_pattern(alias=field_name)} "
    #             f"| {field_name} {{ .*, _id: id({field_name}) }}]"
    #         )
    #     else:
    #         return_query_parts.append(".*")
    #     return_query_parts += [f"_id: id({node_alias})"]
    #     return ', '.join(return_query_parts)
