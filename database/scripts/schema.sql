-- Esquema SQLite de Sortix

CREATE TABLE IF NOT EXISTS rules (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    extension TEXT NOT NULL,       -- sin punto, minusculas, ej. "pdf"
    destination TEXT NOT NULL,     -- ruta relativa a la carpeta personal, ej. "Documents/Facturas"
    rename_pattern TEXT,
    conditions TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_rules_extension ON rules(extension);

CREATE TABLE IF NOT EXISTS moves_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    filename TEXT NOT NULL,
    source TEXT NOT NULL,
    destination TEXT NOT NULL,
    category TEXT NOT NULL,
    moved_at TEXT NOT NULL DEFAULT (datetime('now')),
    undone_at TEXT                 -- fecha en que se deshizo el movimiento, si se deshizo
);

CREATE TABLE IF NOT EXISTS settings (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL
);

-- Temas definidos por el usuario: cualquier cosa (banco, gimnasio, una app
-- concreta...), no solo la universidad. Si el nombre/contenido de un
-- documento contiene alguna de sus palabras clave, se archiva en 'destination'.
CREATE TABLE IF NOT EXISTS topics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,      -- ej. "Banco", "Gimnasio", "Netflix"
    destination TEXT NOT NULL,      -- ruta relativa a la carpeta personal, ej. "Documents/Banco"
    keywords TEXT NOT NULL,         -- palabras clave separadas por comas
    rename_pattern TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
