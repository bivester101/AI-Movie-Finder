import os
import sqlite3
from contextlib import contextmanager

DB_DIR = "data"
DB_PATH = os.path.join(DB_DIR, "app.db")
os.makedirs(DB_DIR, exist_ok=True)

DDL = """
CREATE TABLE IF NOT EXISTS favorites(
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    poster TEXT,
    year TEXT
);
"""

@contextmanager
def _conn():
    con = sqlite3.connect(DB_PATH, check_same_thread=False)
    con.execute(DDL)
    try:
        yield con
        con.commit()
    finally:
        con.close()

def add_fav(mid: int, title: str, poster: str | None, year: str | None) -> None:
    with _conn() as con:
        con.execute(
            "INSERT OR REPLACE INTO favorites(id,title,poster,year) VALUES (?,?,?,?)",
            (mid, title or "", poster or "", year or ""),
        )

def remove_fav(mid: int) -> None:
    with _conn() as con:
        con.execute("DELETE FROM favorites WHERE id=?", (mid,))

def list_favs() -> list[tuple[int, str, str, str]]:
    with _conn() as con:
        rows = con.execute("SELECT id,title,poster,year FROM favorites ORDER BY title").fetchall()
    return rows

def is_fav(mid: int) -> bool:
    with _conn() as con:
        row = con.execute("SELECT 1 FROM favorites WHERE id=?", (mid,)).fetchone()
    return bool(row)

def fav_count() -> int:
    with _conn() as con:
        (n,) = con.execute("SELECT COUNT(*) FROM favorites").fetchone()
    return int(n)
