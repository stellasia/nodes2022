"""Code largely inspired from
https://github.com/neo4j-contrib/neomodel/blob/master/neomodel/util.py#L73
"""
import os

from neo4j import GraphDatabase, basic_auth


class TransactionProxy(object):
    """
    - Ability to have nested with blocks using the same transaction object
    - Count the number of executed queries within a transaction
    """
    def __init__(self, db, access_mode=None):
        self.db = db
        self.access_mode = access_mode
        self.outermost = True

    def __enter__(self):
        self.db.set_connection()
        if self.db._transaction:
            self.outermost = False
            return self
        self.db.begin()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if self.outermost:
            if exc_value:
                self.db.rollback()
                return
            self.db.commit()

    @property
    def queries(self):
        # proxy to db property
        return self.db.queries

    @property
    def number_of_queries(self):
        return len(self.queries)


class Database:
    def __init__(self):
        self.driver = None
        self._transaction = None
        self.queries = []

    def transaction(self, access_mode=None):
        return TransactionProxy(self, access_mode)

    def set_connection(self):
        if self.driver is not None:
            return
        self.driver = GraphDatabase.driver(
            os.getenv("NEO4J_URI", "bolt://127.0.0.1"),
            auth=basic_auth(os.getenv("NEO4J_USER", "neo4j"), os.getenv("NEO4J_PASSWORD", "neo4j")),
        )

    def cypher(self, query, params=None):
        """
        Runs a query on the database and returns a list of results and their headers.

        :param str query: A CYPHER query
        :param dict params: Dictionary of parameters
        :rtype: list
        :returns: list of dict with node properties as keys
        """
        self.set_connection()

        if self._transaction:
            session = self._transaction
        else:
            session = self.driver.session()

        try:
            # Retrieve the data
            response = session.run(query, params)
            keys = response.keys()
            results = []
            for r in response:
                d = dict(zip(keys, r.values()))
                results.append(d)
        except Exception as e:
            raise

        self.queries.append((query, params))

        if not self._transaction:
            session.close()
        return results

    def begin(self, db=None):
        """
        Begins a new transaction, raises SystemError exception if a transaction is in progress
        """
        self.set_connection()
        if self._transaction:
            raise SystemError("Transaction in progress")
        self._transaction = self.driver.session().begin_transaction()
        self.queries = []

    def commit(self):
        """
        Commits the current transaction
        """
        self.set_connection()
        r = None
        try:
            r = self._transaction.commit()
        except Exception as e:
            self.rollback()
        finally:
            self._transaction.close()
            self._transaction = None
            self.queries = []
        return r

    def rollback(self):
        """
        Rolls back the current transaction
        """
        self.set_connection()
        self._transaction.rollback()
        self._transaction = None
        self.queries = []


connection = Database()
