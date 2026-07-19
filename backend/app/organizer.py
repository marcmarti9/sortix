"""Decide el destino final de un archivo (reglas del usuario primero, si no
el clasificador inteligente) y lo mueve de forma segura, sin pisar archivos
con el mismo nombre."""

import shutil
from pathlib import Path

from app import db
from app.classifier import classify
from config.settings import HOME_DIR, IGNORED_SUFFIXES


def resolve_destination_folder(path: Path) -> tuple[str, str]:
    """Devuelve (categoria, carpeta_relativa_a_home) para un archivo dado."""
    ext = path.suffix.lower().lstrip(".")

    rule = db.get_rule_for_extension(ext)
    if rule:
        return "regla personalizada", rule["destination"]

    result = classify(path)
    return result["category"], result["folder"]


def _unique_destination(dest_dir: Path, filename: str) -> Path:
    dest = dest_dir / filename
    if not dest.exists():
        return dest
    stem, suffix = Path(filename).stem, Path(filename).suffix
    counter = 1
    while dest.exists():
        dest = dest_dir / f"{stem} ({counter}){suffix}"
        counter += 1
    return dest


def organize_file(path: Path) -> dict | None:
    """Mueve un archivo a su carpeta correspondiente. Devuelve info del
    movimiento, o None si el archivo ya no existe (p.ej. borrado justo antes)."""
    if not path.exists() or not path.is_file():
        return None

    category, relative_folder = resolve_destination_folder(path)
    
    # Validacion defensiva de Path Traversal
    from app.browser import resolve_safe_path
    dest_dir = resolve_safe_path(relative_folder)
    if dest_dir is None:
        # Fallback a directorio seguro en caso de ruta invalida o maliciosa (ej. ../../etc)
        dest_dir = (HOME_DIR / "Downloads" / "Other").resolve()
        category = f"{category} (insegura redirigida)"
        
    dest_dir.mkdir(parents=True, exist_ok=True)

    destination = _unique_destination(dest_dir, path.name)
    source_str = str(path)
    shutil.move(source_str, str(destination))

    db.log_move(
        filename=path.name,
        source=source_str,
        destination=str(destination),
        category=category,
    )
    return {
        "filename": path.name,
        "source": source_str,
        "destination": str(destination),
        "category": category,
    }


def organize_directory(directory: Path) -> list[dict]:
    """Organiza de golpe todos los archivos ya existentes en una carpeta
    (usado por 'Organizar Ahora')."""
    moved = []
    if not directory.exists():
        return moved
    for entry in sorted(directory.iterdir()):
        if not entry.is_file() or entry.suffix.lower() in IGNORED_SUFFIXES:
            continue
        result = organize_file(entry)
        if result:
            moved.append(result)
    return moved
