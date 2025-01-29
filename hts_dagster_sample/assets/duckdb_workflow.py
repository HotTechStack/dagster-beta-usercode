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


@asset(required_resource_keys={"duckdb_db"})  # Declare the required resource
def run_duckdb_analysis(context, create_analytics_data):  # Use context to access resource
    """Perform DuckDB analysis"""
    db = context.resources.duckdb_db  # Access the resource through context

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