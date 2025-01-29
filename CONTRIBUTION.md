# Dagster Development Guide

## Branch Management

### 1. Creating a New Feature Branch
```bash
# Create and checkout new branch
git checkout -b feature/asset-name
```

Naming conventions:
- `feature/`: New assets or features
- `fix/`: Bug fixes
- `docs/`: Documentation updates
- `refactor/`: Code improvements

### 2. Asset Development Workflow

```bash
# Create new asset file
mkdir -p my_dagster_project/assets/new_domain
touch my_dagster_project/assets/new_domain/__init__.py
touch my_dagster_project/assets/new_domain/assets.py
```

## Asset Development Guide

### 1. Basic Asset Structure
```python
# my_dagster_project/assets/new_domain/assets.py

from dagster import (
    asset,
    AssetIn,
    Output,
    MetadataValue,
    DynamicPartitionsDefinition,
    FreshnessPolicy
)
import pandas as pd
from typing import Optional

@asset(
    description="Description of what this asset does",
    io_manager_key="warehouse_io_manager",  # If using specific storage
    compute_kind="python",  # or "sql", "dbt", etc.
    group_name="domain_name",  # for organizational purposes
    freshness_policy=FreshnessPolicy(
        maximum_lag_minutes=60
    )
)
def my_new_asset() -> pd.DataFrame:
    """
    Detailed documentation about the asset.
    
    Returns:
        pd.DataFrame: Description of return data
    """
    df = pd.DataFrame(...)
    
    return Output(
        df,
        metadata={
            "row_count": len(df),
            "preview": MetadataValue.md(df.head().to_markdown()),
            "schema": MetadataValue.json(df.dtypes.astype(str).to_dict()),
        }
    )
```

### 2. Asset with Dependencies
```python
@asset(
    ins={
        "upstream_data": AssetIn(
            key="upstream_asset",
            description="Data required from upstream"
        )
    }
)
def dependent_asset(upstream_data: pd.DataFrame) -> pd.DataFrame:
    """
    Process data from upstream asset.
    """
    result_df = upstream_data.copy()
    # Processing logic
    return result_df
```

### 3. Reading Different Data Sources

#### CSV Files
```python
@asset
def read_csv_data() -> pd.DataFrame:
    """Read data from CSV file."""
    df = pd.read_csv(
        "path/to/file.csv",
        parse_dates=["date_column"],
        dtype={
            "string_col": str,
            "int_col": int
        }
    )
    
    # Validate data
    assert not df.empty, "CSV data is empty"
    assert all(df.columns == ["expected", "columns"]), "Unexpected columns"
    
    return Output(
        df,
        metadata={
            "row_count": len(df),
            "preview": MetadataValue.md(df.head().to_markdown()),
            "columns": MetadataValue.json(list(df.columns)),
        }
    )
```

#### Database Tables
```python
@asset(
    required_resource_keys={"database"}
)
def read_db_table(context) -> pd.DataFrame:
    """Read data from database table."""
    query = """
    SELECT *
    FROM my_table
    WHERE date_column >= CURRENT_DATE - INTERVAL '7 days'
    """
    
    with context.resources.database.get_connection() as conn:
        df = pd.read_sql(query, conn)
    
    return Output(
        df,
        metadata={
            "row_count": len(df),
            "date_range": f"{df['date_column'].min()} to {df['date_column'].max()}"
        }
    )
```

#### Partitioned Data
```python
date_partitions = DynamicPartitionsDefinition(name="date")

@asset(
    partitions_def=date_partitions,
    description="Process data for specific date"
)
def date_partitioned_asset(context) -> pd.DataFrame:
    """Process data for a specific date partition."""
    partition_date = context.asset_partition_key_for_output()
    
    # Read data for specific partition
    df = pd.read_parquet(f"path/to/data/date={partition_date}")
    
    return Output(
        df,
        metadata={
            "partition": partition_date,
            "row_count": len(df)
        }
    )
```

### 4. Writing Data Assets

#### To Data Warehouse
```python
@asset(
    io_manager_key="warehouse_io_manager",
    key_prefix=["raw", "sales"]  # Creates raw.sales.my_table
)
def write_to_warehouse(data: pd.DataFrame) -> pd.DataFrame:
    """
    Write data to warehouse.
    The io_manager will handle the actual writing.
    """
    return Output(
        data,
        metadata={
            "schema": MetadataValue.json(data.dtypes.astype(str).to_dict()),
            "row_count": len(data)
        }
    )
```

#### To Multiple Outputs
```python
from dagster import Out, DynamicOutput, DynamicOut

@asset(
    outs={
        "valid_data": Out(description="Valid records"),
        "error_data": Out(description="Records with issues")
    }
)
def process_with_validation(data: pd.DataFrame):
    """Process data and separate valid/invalid records."""
    valid_mask = data["value"].notna()
    
    valid_df = data[valid_mask]
    error_df = data[~valid_mask]
    
    return {
        "valid_data": Output(
            valid_df,
            metadata={"row_count": len(valid_df)}
        ),
        "error_data": Output(
            error_df,
            metadata={"row_count": len(error_df)}
        )
    }
```

## Testing Assets

### 1. Unit Tests
```python
# tests/assets/test_new_domain.py

def test_my_new_asset():
    """Test my_new_asset processing logic."""
    # Given
    test_data = pd.DataFrame(...)
    
    # When
    result = my_new_asset()
    
    # Then
    assert not result.empty
    assert list(result.columns) == ["expected", "columns"]
    assert result["value"].notna().all()
```

### 2. Integration Tests
```python
from dagster import build_op_context, materialize

def test_asset_with_dependencies():
    """Test asset with its dependencies."""
    context = build_op_context(
        resources={
            "database": MockDatabaseResource()
        }
    )
    
    result = materialize(
        [dependent_asset],
        resources={"database": MockDatabaseResource()}
    )
    
    assert result.success
```

## Best Practices

1. **Naming Conventions**:
   - Use descriptive names for assets
   - Group related assets in subdirectories
   - Use consistent naming patterns

2. **Documentation**:
   - Always include docstrings
   - Document input/output data structures
   - Explain business logic and assumptions

3. **Data Quality**:
   - Add data validation checks
   - Include row counts and previews in metadata
   - Log important statistics

4. **Performance**:
   - Use appropriate data types
   - Consider partitioning for large datasets
   - Add appropriate indexes

5. **Testing**:
   - Write unit tests for processing logic
   - Add integration tests for dependencies
   - Test edge cases and error conditions

## Committing Changes
```bash
# Add and commit changes
git add my_dagster_project/assets/new_domain
git commit -m "feat: Add new domain assets for X"

# Push to remote branch
git push origin feature/asset-name

# Create Pull Request
# Use the GitHub UI to create PR from your branch to main
```