import sqlite3

create_table = """
CREATE TABLE IF NOT EXISTS trades (
  trade_id TEXT PRIMARY KEY,
  type TEXT,
  open_or_close TEXT,
  qty REAL,
  price REAL,
  btc_bal REAL,
  usdt_bal REAL,
  date datetime
);
"""


def init_conn(db_path):
    conn = None
    try:
        conn = sqlite3.connect(db_path)

    except sqlite3.Error as e:
        print(e)

    return conn


def execute_query(conn, query):
    try:
        conn.execute(query)
        conn.commit()
        return True

    except sqlite3.Error as e:
        print(e)
        return False
