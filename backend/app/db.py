"""Acceso a la base de datos SQLite: reglas del usuario, log de movimientos
y ajustes persistentes (p.ej. si la Patrulla Activa estaba encendida)."""

import sqlite3
from contextlib import contextmanager

from config.settings import DB_PATH, SCHEMA_PATH


def init_db() -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with get_conn() as conn:
        conn.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))


@contextmanager
def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA journal_mode = WAL")
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


# ---- reglas personalizadas -------------------------------------------------

def list_rules() -> list[dict]:
    with get_conn() as conn:
        rows = conn.execute("SELECT * FROM rules ORDER BY extension").fetchall()
        return [dict(r) for r in rows]


def add_rule(extension: str, destination: str) -> dict:
    extension = extension.lower().lstrip(".").strip()
    destination = destination.strip().strip("/")
    with get_conn() as conn:
        conn.execute(
            """INSERT INTO rules (extension, destination) VALUES (?, ?)
               ON CONFLICT(extension) DO UPDATE SET destination = excluded.destination""",
            (extension, destination),
        )
        row = conn.execute("SELECT * FROM rules WHERE extension = ?", (extension,)).fetchone()
        return dict(row)


def delete_rule(rule_id: int) -> None:
    with get_conn() as conn:
        conn.execute("DELETE FROM rules WHERE id = ?", (rule_id,))


def get_rule_for_extension(extension: str) -> dict | None:
    with get_conn() as conn:
        row = conn.execute(
            "SELECT * FROM rules WHERE extension = ?", (extension.lower().lstrip("."),)
        ).fetchone()
        return dict(row) if row else None


# ---- log de movimientos / estadisticas -------------------------------------

def log_move(filename: str, source: str, destination: str, category: str) -> None:
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO moves_log (filename, source, destination, category) VALUES (?, ?, ?, ?)",
            (filename, source, destination, category),
        )


def count_moves() -> int:
    with get_conn() as conn:
        row = conn.execute("SELECT COUNT(*) AS c FROM moves_log").fetchone()
        return row["c"]


def recent_moves(limit: int = 20) -> list[dict]:
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT * FROM moves_log ORDER BY id DESC LIMIT ?", (limit,)
        ).fetchall()
        return [dict(r) for r in rows]


# ---- ajustes ----------------------------------------------------------------

def get_setting(key: str, default: str | None = None) -> str | None:
    with get_conn() as conn:
        row = conn.execute("SELECT value FROM settings WHERE key = ?", (key,)).fetchone()
        return row["value"] if row else default


def set_setting(key: str, value: str) -> None:
    with get_conn() as conn:
        conn.execute(
            """INSERT INTO settings (key, value) VALUES (?, ?)
               ON CONFLICT(key) DO UPDATE SET value = excluded.value""",
            (key, value),
        )


# ---- temas (topics) ----------------------------------------------------------

def _topic_row_to_dict(row: sqlite3.Row) -> dict:
    d = dict(row)
    d["keywords"] = [k.strip() for k in d["keywords"].split(",") if k.strip()]
    return d


def list_topics() -> list[dict]:
    with get_conn() as conn:
        rows = conn.execute("SELECT * FROM topics ORDER BY name").fetchall()
        return [_topic_row_to_dict(r) for r in rows]


def add_topic(name: str, destination: str, keywords: list[str]) -> dict:
    name = name.strip()
    destination = destination.strip().strip("/")
    keywords_str = ",".join(k.strip() for k in keywords if k.strip())
    with get_conn() as conn:
        conn.execute(
            """INSERT INTO topics (name, destination, keywords) VALUES (?, ?, ?)
               ON CONFLICT(name) DO UPDATE SET destination = excluded.destination,
                                                keywords = excluded.keywords""",
            (name, destination, keywords_str),
        )
        row = conn.execute("SELECT * FROM topics WHERE name = ?", (name,)).fetchone()
        return _topic_row_to_dict(row)


def delete_topic(topic_id: int) -> None:
    with get_conn() as conn:
        conn.execute("DELETE FROM topics WHERE id = ?", (topic_id,))
