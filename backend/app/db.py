"""Acceso a la base de datos SQLite: reglas del usuario, log de movimientos
y ajustes persistentes (p.ej. si la Patrulla Activa estaba encendida)."""

import sqlite3
from contextlib import contextmanager

from config.settings import DB_PATH, SCHEMA_PATH


def init_db() -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with get_conn() as conn:
        pass  # get_conn ya garantiza el esquema


def _ensure_schema(conn: sqlite3.Connection) -> None:
    """Crea las tablas si faltan. Se comprueba en cada conexion (un SELECT
    trivial) para sobrevivir a que alguien borre o vacie martix.db con el
    servidor en marcha: la siguiente peticion lo regenera en vez de dar 500."""
    required = {"rules", "moves_log", "settings", "topics", "maintenance_rules", "watched_folders"}
    existing = {
        row["name"]
        for row in conn.execute("SELECT name FROM sqlite_master WHERE type = 'table'")
    }
    if not required.issubset(existing):
        conn.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))
    _migrate(conn)


def _migrate(conn: sqlite3.Connection) -> None:
    """Migraciones para bases de datos creadas con esquemas anteriores."""
    columns = {row["name"] for row in conn.execute("PRAGMA table_info(moves_log)")}
    if "undone_at" not in columns:
        conn.execute("ALTER TABLE moves_log ADD COLUMN undone_at TEXT")

    rules_cols = {row["name"] for row in conn.execute("PRAGMA table_info(rules)")}
    if "rename_pattern" not in rules_cols:
        conn.execute("ALTER TABLE rules ADD COLUMN rename_pattern TEXT")
    if "conditions" not in rules_cols:
        conn.execute("ALTER TABLE rules ADD COLUMN conditions TEXT")

    topics_cols = {row["name"] for row in conn.execute("PRAGMA table_info(topics)")}
    if "rename_pattern" not in topics_cols:
        conn.execute("ALTER TABLE topics ADD COLUMN rename_pattern TEXT")

    existing_tables = {
        row["name"]
        for row in conn.execute("SELECT name FROM sqlite_master WHERE type = 'table'")
    }
    if "maintenance_rules" in existing_tables:
        m_cols = {row["name"] for row in conn.execute("PRAGMA table_info(maintenance_rules)")}
        if "folder" not in m_cols:
            conn.execute("DROP TABLE maintenance_rules")
            conn.execute("""
                CREATE TABLE maintenance_rules (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    folder TEXT NOT NULL UNIQUE,
                    max_age_days INTEGER NOT NULL,
                    active INTEGER NOT NULL DEFAULT 1,
                    created_at TEXT NOT NULL DEFAULT (datetime('now'))
                )
            """)
    else:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS maintenance_rules (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                folder TEXT NOT NULL UNIQUE,
                max_age_days INTEGER NOT NULL,
                active INTEGER NOT NULL DEFAULT 1,
                created_at TEXT NOT NULL DEFAULT (datetime('now'))
            )
        """)

    if "watched_folders" not in existing_tables:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS watched_folders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                folder_path TEXT NOT NULL UNIQUE,
                active INTEGER NOT NULL DEFAULT 1,
                created_at TEXT NOT NULL DEFAULT (datetime('now'))
            )
        """)



@contextmanager
def get_conn():
    conn = sqlite3.connect(DB_PATH, timeout=10)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA journal_mode = WAL")
    conn.execute("PRAGMA busy_timeout = 5000")
    try:
        _ensure_schema(conn)
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


# ---- reglas personalizadas -------------------------------------------------

def list_rules() -> list[dict]:
    # organizer.resolve_destination_folder toma la primera regla que
    # coincide, asi que las reglas comodin ("*") deben ir siempre despues de
    # las de extension concreta: por orden ASCII normal "*" (42) ordena antes
    # que cualquier letra o digito y silenciaria toda regla especifica.
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT * FROM rules ORDER BY (extension = '*'), extension"
        ).fetchall()
        return [dict(r) for r in rows]


def add_rule(extension: str, destination: str, rename_pattern: str | None = None, conditions: str | None = None) -> dict:
    extension = extension.lower().lstrip(".").strip()
    destination = destination.strip().strip("/")
    with get_conn() as conn:
        conn.execute(
            """INSERT INTO rules (extension, destination, rename_pattern, conditions) VALUES (?, ?, ?, ?)
               ON CONFLICT(extension) DO UPDATE SET destination = excluded.destination,
                                                    rename_pattern = excluded.rename_pattern,
                                                    conditions = excluded.conditions""",
            (extension, destination, rename_pattern, conditions),
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
    limit = max(1, min(limit, 500))
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT * FROM moves_log ORDER BY id DESC LIMIT ?", (limit,)
        ).fetchall()
        return [dict(r) for r in rows]


def get_move(move_id: int) -> dict | None:
    with get_conn() as conn:
        row = conn.execute("SELECT * FROM moves_log WHERE id = ?", (move_id,)).fetchone()
        return dict(row) if row else None


def mark_move_undone(move_id: int) -> None:
    with get_conn() as conn:
        conn.execute(
            "UPDATE moves_log SET undone_at = datetime('now') WHERE id = ?", (move_id,)
        )


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


def add_topic(name: str, destination: str, keywords: list[str], rename_pattern: str | None = None) -> dict:
    name = name.strip()
    destination = destination.strip().strip("/")
    keywords_str = ",".join(k.strip() for k in keywords if k.strip())
    with get_conn() as conn:
        conn.execute(
            """INSERT INTO topics (name, destination, keywords, rename_pattern) VALUES (?, ?, ?, ?)
               ON CONFLICT(name) DO UPDATE SET destination = excluded.destination,
                                                keywords = excluded.keywords,
                                                rename_pattern = excluded.rename_pattern""",
            (name, destination, keywords_str, rename_pattern),
        )
        row = conn.execute("SELECT * FROM topics WHERE name = ?", (name,)).fetchone()
        return _topic_row_to_dict(row)


def delete_topic(topic_id: int) -> None:
    with get_conn() as conn:
        conn.execute("DELETE FROM topics WHERE id = ?", (topic_id,))


# ---- maintenance rules -------------------------------------------------------

def list_maintenance_rules() -> list[dict]:
    with get_conn() as conn:
        rows = conn.execute("SELECT * FROM maintenance_rules ORDER BY folder").fetchall()
        result = []
        for r in rows:
            d = dict(r)
            d["directory_path"] = d["folder"]
            result.append(d)
        return result


def add_maintenance_rule(folder: str, max_age_days: int, active: int = 1) -> dict:
    folder = folder.strip()
    with get_conn() as conn:
        conn.execute(
            """INSERT INTO maintenance_rules (folder, max_age_days, active) VALUES (?, ?, ?)
               ON CONFLICT(folder) DO UPDATE SET max_age_days = excluded.max_age_days, active = excluded.active""",
            (folder, max_age_days, active),
        )
        row = conn.execute("SELECT * FROM maintenance_rules WHERE folder = ?", (folder,)).fetchone()
        d = dict(row)
        d["directory_path"] = d["folder"]
        return d


def delete_maintenance_rule(rule_id: int) -> None:
    with get_conn() as conn:
        conn.execute("DELETE FROM maintenance_rules WHERE id = ?", (rule_id,))


# ---- watched folders ---------------------------------------------------------

def list_watched_folders() -> list[dict]:
    with get_conn() as conn:
        rows = conn.execute("SELECT * FROM watched_folders ORDER BY folder_path").fetchall()
        return [dict(r) for r in rows]


def add_watched_folder(folder_path: str, active: int = 1) -> dict:
    folder_path = folder_path.strip()
    with get_conn() as conn:
        conn.execute(
            """INSERT INTO watched_folders (folder_path, active) VALUES (?, ?)
               ON CONFLICT(folder_path) DO UPDATE SET active = excluded.active""",
            (folder_path, active),
        )
        row = conn.execute("SELECT * FROM watched_folders WHERE folder_path = ?", (folder_path,)).fetchone()
        return dict(row)


def delete_watched_folder(folder_id: int) -> None:
    with get_conn() as conn:
        conn.execute("DELETE FROM watched_folders WHERE id = ?", (folder_id,))


# ---- statistics dashboard ----------------------------------------------------

def get_statistics() -> dict:
    with get_conn() as conn:
        total = conn.execute('SELECT COUNT(*) AS c FROM moves_log WHERE undone_at IS NULL').fetchone()['c']
        by_category = conn.execute('SELECT category, COUNT(*) AS c FROM moves_log WHERE undone_at IS NULL GROUP BY category ORDER BY c DESC').fetchall()
        by_day = conn.execute("SELECT date(moved_at) AS day, COUNT(*) AS c FROM moves_log WHERE undone_at IS NULL GROUP BY day ORDER BY day DESC LIMIT 30").fetchall()
        return {
            'total_organized': total,
            'by_category': [dict(r) for r in by_category],
            'by_day': [dict(r) for r in reversed(by_day)],
        }

