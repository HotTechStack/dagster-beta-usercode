from dagster import asset, Output, MetadataValue
import pandas as pd
import numpy as np
from datetime import datetime, timedelta


@asset
def generate_sales():
    """Generate synthetic sales data"""
    start_date = datetime.now() - timedelta(days=365)
    dates = [start_date + timedelta(days=x) for x in range(365)]

    np.random.seed(42)
    df = pd.DataFrame({
        'date': dates,
        'sales': np.random.normal(1000, 200, 365),
        'customers': np.random.poisson(100, 365)
    })

    return Output(
        df,
        metadata={
            "rows": len(df),
            "preview": MetadataValue.md(df.head().to_markdown())
        }
    )


@asset
def analyze_sales(generate_sales):
    """Analyze sales patterns"""
    df = generate_sales.copy()

    # Add time-based features
    df['day_of_week'] = df['date'].dt.day_name()
    df['month'] = df['date'].dt.month
    df['is_weekend'] = df['day_of_week'].isin(['Saturday', 'Sunday'])

    # Calculate monthly stats
    monthly_stats = df.groupby('month').agg({
        'sales': ['mean', 'std'],
        'customers': 'sum'
    }).round(2)

    return Output(
        monthly_stats,
        metadata={
            "rows": len(monthly_stats),
            "preview": MetadataValue.md(monthly_stats.head().to_markdown())
        }
    )
