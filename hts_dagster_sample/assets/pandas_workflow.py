from dagster import asset, Output, MetadataValue
import pandas as pd
import requests


@asset
def fetch_stock_data():
    """Fetch stock market data using pandas"""
    symbol = "AAPL"
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"

    response = requests.get(url)
    data = response.json()

    df = pd.DataFrame({
        'timestamp': pd.to_datetime(data['chart']['result'][0]['timestamp'], unit='s'),
        'close': data['chart']['result'][0]['indicators']['quote'][0]['close']
    })

    return Output(
        df,
        metadata={
            "rows": len(df),
            "preview": MetadataValue.md(df.head().to_markdown())
        }
    )


@asset
def calculate_stock_metrics(fetch_stock_data):
    """Calculate moving averages"""
    df = fetch_stock_data.copy()
    df['MA5'] = df['close'].rolling(window=5).mean()
    df['MA20'] = df['close'].rolling(window=20).mean()

    return Output(
        df,
        metadata={
            "rows": len(df),
            "preview": MetadataValue.md(df.head().to_markdown())
        }
    )
