BINANCE_KLINES_URL = "https://api.binance.com/api/v3/klines"
DB_URL = "postgresql://user:pass@host:5432/db"
TABLE_NAME = "klines"

KLINE_COLUMNS = [
    "open_time", "open", "high", "low", "close", "volume",
    "close_time", "quote_asset_volume", "num_trades",
    "taker_buy_base_volume", "taker_buy_quote_volume", "ignore",
]