from dagster import Definitions
from .resources.database import postgres_db, duckdb_db

defs = Definitions(
    assets=[],  # Assets are auto-discovered
    resources={
        "postgres_db": postgres_db,
        "duckdb_db": duckdb_db,
    }
)