"""Carga la configuracion de Martix: variables de entorno (.env), rutas base
y el fichero de categorias. Sin dependencias externas para que corra en
cualquier maquina modesta."""

import json
import sys
from pathlib import Path

if getattr(sys, "frozen", False):
    BASE_DIR = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))
    PROJECT_DIR = BASE_DIR
    BACKEND_DIR = BASE_DIR / "backend" if (BASE_DIR / "backend").exists() else BASE_DIR
    CONFIG_DIR = BASE_DIR / "config" if (BASE_DIR / "config").exists() else BASE_DIR
else:
    BACKEND_DIR = Path(__file__).resolve().parent.parent
    PROJECT_DIR = BACKEND_DIR.parent
    CONFIG_DIR = Path(__file__).resolve().parent

CATEGORIES_FILE = CONFIG_DIR / "categories.json"

DB_PATH = PROJECT_DIR / "database" / "martix.db"
_OLD_DB_PATH = PROJECT_DIR / "database" / "sortix.db"
if not DB_PATH.exists() and _OLD_DB_PATH.exists():
    try:
        _OLD_DB_PATH.rename(DB_PATH)
    except Exception:
        pass

SCHEMA_PATH = PROJECT_DIR / "database" / "scripts" / "schema.sql"


def _load_env(env_path: Path) -> dict:
    """Parser minimo de .env (KEY=VALUE), sin depender de python-dotenv."""
    values = {}
    if not env_path.exists():
        return values
    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        values[key.strip()] = value.strip().strip('"').strip("'")
    return values


_env = _load_env(BACKEND_DIR / ".env")

HOST = _env.get("HOST", "127.0.0.1")
PORT = int(_env.get("PORT", "5000"))

_downloads_override = _env.get("DOWNLOADS_DIR", "").strip()
DOWNLOADS_DIR = Path(_downloads_override).expanduser() if _downloads_override else Path.home() / "Downloads"

HOME_DIR = Path.home()

# Token compartido para la API (cabecera X-Martix-Token). Opcional mientras
# Martix escuche solo en 127.0.0.1; obligatorio si se expone HOST a la red.
API_TOKEN = _env.get("MARTIX_TOKEN", _env.get("SORTIX_TOKEN", "")).strip()


def _env_flag(name: str) -> bool:
    return _env.get(name, "").strip().lower() in {"1", "true", "yes", "on"}


# LLM local (Ollama) para nombrar carpetas de documentos que no encajan en
# ningun Tema ni subcategoria. Apagado por defecto: en equipos modestos no
# se nota nada y todo sigue funcionando por reglas/patrones.
LLM_ENABLED = _env_flag("MARTIX_LLM") or _env_flag("SORTIX_LLM")
LLM_URL = _env.get("MARTIX_LLM_URL", _env.get("SORTIX_LLM_URL", "http://127.0.0.1:11434"))
LLM_MODEL = _env.get("MARTIX_LLM_MODEL", _env.get("SORTIX_LLM_MODEL", "llama3.2"))

import time

# Extensiones y prefijos de archivos temporales/parciales de navegadores
IGNORED_SUFFIXES = {
    ".crdownload",
    ".part",
    ".tmp",
    ".temp",
    ".download",
    ".partial",
    ".opdownload",
    ".fdown",
    ".utether",
    ".filepart",
}

IGNORED_PREFIXES = (
    "unconfirmed",
    "drive-download-",
    ".com.google.chrome",
    ".org.chromium",
    "~$",
    ".~",
)


def is_temporary_download_file(path: Path) -> bool:
    """Comprueba si un archivo es un artefacto temporal o parcial de descarga del navegador."""
    name_lower = path.name.lower()
    suffix_lower = path.suffix.lower()

    if suffix_lower in IGNORED_SUFFIXES:
        return True

    for pref in IGNORED_PREFIXES:
        if name_lower.startswith(pref):
            return True

    if ".crdownload" in name_lower or ".part" in name_lower:
        return True

    return False


def is_file_in_use(path: Path) -> bool:
    """Comprueba si un archivo está siendo escrito o mantenido abierto por otra aplicación (p.ej. el navegador)."""
    if not path.exists() or not path.is_file():
        return False

    # Prueba de apertura/bloqueo exclusivo de archivo
    if sys.platform == "win32":
        try:
            with open(path, "r+b"):
                pass
        except (PermissionError, OSError):
            return True
    else:
        try:
            import fcntl
            with open(path, "r+b") as f:
                try:
                    fcntl.flock(f.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                    fcntl.flock(f.fileno(), fcntl.LOCK_UN)
                except (IOError, OSError):
                    return True
        except (PermissionError, OSError):
            return True

    return False


def load_categories() -> dict:
    with open(CATEGORIES_FILE, encoding="utf-8") as f:
        return json.load(f)
