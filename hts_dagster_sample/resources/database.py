from dagster import resource
import duckdb
import psycopg2
from contextlib import contextmanager

class PostgresDB:
    def __init__(self, conn_string):
        self.conn_string = conn_string

    @contextmanager
    def get_connection(self):
        conn = psycopg2.connect(self.conn_string)
        try:
            yield conn
        finally:
            conn.close()

@resource(config_schema={"conn_string": str})
def postgres_db(context):
    return PostgresDB(context.resource_config["conn_string"])

@resource(config_schema={"path": str})
def duckdb_db(context):
    return duckdb.connect(context.resource_config["path"])