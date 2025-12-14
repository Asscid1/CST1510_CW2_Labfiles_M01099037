import sqlite3
import pandas as pd
from pathlib import Path

DATA_DIR = Path("DATA")
DB_PATH = DATA_DIR / "intelligence_platform.db"


def connect_database(db_path=DB_PATH):
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(str(db_path))

    conn.execute("PRAGMA foreign_keys = ON")

    return conn


def load_csv_to_table(conn, csv_path, table_name):
    path = Path(csv_path)
    if not path.exists():
        print(f"Warning: {csv_path} not found.")
        return 0

    df = pd.read_csv(path)
    df.to_sql(name=table_name, con=conn, if_exists="append", index=False)
    print(f"Loaded {len(df)} rows into {table_name}")
    return len(df)


def close_connection(conn):
    if conn:
        conn.close()
