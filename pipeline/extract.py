"""
Simple Binance ETL pipeline
============================
Extract  : Pull candlestick (kline) data from Binance's public REST API
Transform: Clean types, add derived columns (returns, typical price, etc.)
Load     : Upsert into a SQL database (SQLite by default; swap the engine
           URL to use Postgres/MySQL/etc.)

No API key is required for public market data.

Usage:
    python etl.py                       # defaults: BTCUSDT, 1h candles, last 500
    python etl.py --symbol ETHUSDT --interval 15m --limit 1000
"""



import pandas as pd
import requests

from .config import BINANCE_KLINES_URL



def extract(symbol: str, interval: str, limit: int) -> list:
    """Fetch raw kline (candlestick) data from Binance's public REST API."""
    params = {"symbol": symbol.upper(), "interval": interval, "limit": limit}
    resp = requests.get(BINANCE_KLINES_URL, params=params, timeout=10)
    resp.raise_for_status()
    data = resp.json()
    if not data:
        raise ValueError(f"No data returned for {symbol} / {interval}")
    return data
