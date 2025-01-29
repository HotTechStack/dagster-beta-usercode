from dagster import asset, Output, MetadataValue
import polars as pl
import requests
from io import StringIO


@asset
def fetch_weather_data():
    """Fetch weather data using Polars"""
    url = "https://raw.githubusercontent.com/jbrownlee/Datasets/master/daily-min-temperatures.csv"
    response = requests.get(url)

    df = pl.read_csv(StringIO(response.text))
    return Output(
        df,
        metadata={
            "rows": len(df),
            "preview": MetadataValue.md(df.head().to_markdown())
        }
    )


@asset
def analyze_weather(fetch_weather_data):
    """Analyze weather patterns"""
    df = fetch_weather_data
    monthly_stats = df.groupby(
        pl.col("Date").str.strptime(pl.Date, fmt="%Y-%m-%d").dt.month()
    ).agg([
        pl.col("Temp").mean().alias("avg_temp"),
        pl.col("Temp").min().alias("min_temp"),
        pl.col("Temp").max().alias("max_temp")
    ])

    return Output(
        monthly_stats,
        metadata={
            "rows": len(monthly_stats),
            "preview": MetadataValue.md(monthly_stats.head().to_markdown())
        }
    )