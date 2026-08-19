import pandas as pd
from datetime import datetime, timezone

from .config import KLINE_COLUMNS

def transform(raw: list, symbol: str, interval: str) -> pd.DataFrame:
    """Turn raw Binance rows into a clean, typed DataFrame with a few
    derived columns useful for downstream analysis."""
    df = pd.DataFrame(raw, columns=KLINE_COLUMNS)
    df.drop(columns=["ignore"], inplace=True)

    # Types
    numeric_cols = [
        "open", "high", "low", "close", "volume",
        "quote_asset_volume", "taker_buy_base_volume", "taker_buy_quote_volume",
    ]
    df[numeric_cols] = df[numeric_cols].astype(float)
    df["num_trades"] = df["num_trades"].astype(int)

    # Stored as naive UTC (tz stripped) rather than tz-aware. This is a
    # deliberate choice: SQLite has no native datetime type, and different
    # DBAPI drivers serialize tz-aware datetimes to text inconsistently
    # (some include a "+00:00" offset, some don't), which silently breaks
    # equality comparisons used for dedup below. All timestamps here are UTC.
    df["open_time"] = pd.to_datetime(df["open_time"], unit="ms", utc=True).dt.tz_localize(None)
    df["close_time"] = pd.to_datetime(df["close_time"], unit="ms", utc=True).dt.tz_localize(None)

    # Metadata
    df.insert(0, "symbol", symbol.upper())
    df.insert(1, "interval", interval)

    # Derived fields
    df["typical_price"] = (df["high"] + df["low"] + df["close"]) / 3
    df["pct_change"] = (df["close"] - df["open"]) / df["open"] * 100
    df["loaded_at"] = datetime.now(timezone.utc).replace(tzinfo=None)

    print(df)
    return df

