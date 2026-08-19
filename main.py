import argparse
import sys
import requests

from pipeline.extract import extract
from pipeline.transform import transform
from pipeline.load import load

from pipeline.config import DB_URL, TABLE_NAME

def run_pipeline(symbol: str, interval: str, limit: int, db_url: str = DB_URL) -> None:
    print(f"[extract]  Fetching {limit} x {interval} candles for {symbol} ...")
    raw = extract(symbol, interval, limit)

    print("[transform] Cleaning and enriching data ...")
    df = transform(raw, symbol, interval)

    print(f"[load]     Writing {len(df)} rows to {db_url} (table: {TABLE_NAME}) ...")
    n = load(df, db_url)

    print(f"Done. {n} rows loaded.")
    print(df[["symbol", "interval", "open_time", "close", "volume", "pct_change"]].tail())


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Simple Binance ETL pipeline")
    parser.add_argument("--symbol", default="BTCUSDT", help="Trading pair, e.g. BTCUSDT")
    parser.add_argument("--interval", default="1h",
                         help="Candle interval: 1m, 5m, 15m, 1h, 4h, 1d, ...")
    parser.add_argument("--limit", type=int, default=500, help="Number of candles (max 1000)")
    parser.add_argument("--db-url", default=DB_URL, help="SQLAlchemy database URL")
    args = parser.parse_args()

    try:
        run_pipeline(args.symbol, args.interval, args.limit, args.db_url)
    except requests.exceptions.RequestException as e:
        print(f"Network/API error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Pipeline failed: {e}", file=sys.stderr)
        sys.exit(1)