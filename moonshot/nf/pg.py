"""The Moonshot PostgreSQL publication layer (C-012-T002). RED stub: the API the tests use, nothing implemented."""

SCHEMA_VERSION = 1
ROLES = ("reader", "coordinator", "publisher", "validator", "resolver")


def connect():
    raise NotImplementedError("C-012-T002")


def init_schema(conn, schema="moonshot"):
    raise NotImplementedError("C-012-T002")


def drop_schema(conn, schema):
    pass


class Moonshot:
    def __init__(self, conn, schema="moonshot", role="reader", actor=""):
        self.conn, self.schema, self.role, self.actor = conn, schema, role, actor

    def close(self):
        pass

    def __getattr__(self, name):
        raise NotImplementedError("C-012-T002: Moonshot.{}".format(name))
