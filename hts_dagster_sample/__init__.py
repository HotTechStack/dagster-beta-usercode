from dagster import Definitions, load_assets_from_modules
from hts_dagster_sample.assets import (
    duckdb_workflow,
    pandas_workflow,
    polars_workflow,
    postgres_workflow,
    sales_workflow
)
from hts_dagster_sample.resources.database import postgres_db, duckdb_db

# Load assets from modules using load_assets_from_modules
duckdb_assets = load_assets_from_modules([duckdb_workflow])
pandas_assets = load_assets_from_modules([pandas_workflow])
polars_assets = load_assets_from_modules([polars_workflow])
postgres_assets = load_assets_from_modules([postgres_workflow])
sales_assets = load_assets_from_modules([sales_workflow])

# Combine all assets
all_assets = [
    *duckdb_assets,
    *pandas_assets,
    *polars_assets,
    *postgres_assets,
    *sales_assets,
]

# Define your Dagster definitions with the resources
defs = Definitions(
    assets=all_assets,
    resources={
        "duckdb_db": duckdb_db.configured({
            "path": ":memory:"  # or a specific file path
        }),
        "postgres": postgres_db.configured({
            "conn_string": "postgresql://username:password@host:5432/dbname"
        })
    }
)