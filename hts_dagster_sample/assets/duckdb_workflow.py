from dagster import asset, Output, MetadataValue
import pandas as pd


@asset
def create_analytics_data():
    """Create sample data for analytics"""
    df = pd.DataFrame({
        'id': range(1000),
        'value': range(1000),
        'category': ['A', 'B', 'C', 'D'] * 250
    })
    return df


@asset
def run_duckdb_analysis(create_analytics_data, duckdb_db):
    """Perform DuckDB analysis"""
    db = duckdb_db

    # Register DataFrame as table
    db.register('analytics_data', create_analytics_data)

    # Run analysis
    query = """
    SELECT 
        category,
        COUNT(*) as count,
        AVG(value) as avg_value
    FROM analytics_data
    GROUP BY category
    ORDER BY category
    """

    result = db.execute(query).fetch_df()
    return Output(
        result,
        metadata={
            "rows": len(result),
            "preview": MetadataValue.md(result.to_markdown())
        }
    )