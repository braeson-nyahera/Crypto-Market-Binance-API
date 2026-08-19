import pandas as pd 
from sqlalchemy import create_engine, text

from .config import DB_URL, TABLE_NAME

def load(df: pd.DataFrame, db_url: str = DB_URL, table: str = TABLE_NAME) -> int:
    """Load the transformed data into the database.

    Uses a delete+insert per (symbol, interval, open_time) to avoid
    duplicate rows when the pipeline is re-run on overlapping ranges.
    """
    engine = create_engine(db_url)

    with engine.begin() as conn:
        df.head(0).to_sql(table, conn, if_exists="append", index=False)

        # Drop any rows that would collide (basic idempotency), one row at a
        # time via bound parameters. This is deliberately dialect-agnostic:
        # SQLAlchemy handles the Python datetime -> column type conversion
        # itself, so it works the same on SQLite, Postgres, MySQL, etc.
        # (A BETWEEN/range delete or relying on string-formatted timestamps
        # is fragile because different backends/drivers serialize datetimes
        # differently -- that mismatch is what caused this to silently no-op
        # during testing, so it's avoided here on purpose.)
        symbol = df["symbol"].iloc[0]
        interval = df["interval"].iloc[0]
        delete_stmt = text(
            f"DELETE FROM {table} WHERE symbol = :symbol AND interval = :interval AND open_time = :open_time"
        )
        params = [
            {"symbol": symbol, "interval": interval, "open_time": t.to_pydatetime().replace(tzinfo=None)}
            for t in df["open_time"]
        ]
        conn.execute(delete_stmt, params)

    df.to_sql(table, engine, if_exists="append", index=False)
    return len(df)
