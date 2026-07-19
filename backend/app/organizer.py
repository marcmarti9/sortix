"""Decide el destino final de un archivo (reglas del usuario primero, si no
el clasificador inteligente), lo mueve de forma segura sin pisar archivos
con el mismo nombre, y permite deshacer un movimiento del historial."""

import logging
import shutil
from pathlib import Path

from app import db
from app.classifier import classify
from app.security import safe_destination_dir
from config.settings import IGNORED_SUFFIXES

logger = logging.getLogger("sortix.organizer")


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
    movimiento, o None si no se movio (ya no existe, destino invalido,
    o ya esta en su carpeta de destino)."""
    if not path.exists() or not path.is_file():
        return None

    category, relative_folder = resolve_destination_folder(path)

    dest_dir = safe_destination_dir(relative_folder)
    if dest_dir is None:
        logger.warning("destino invalido %r para %s; no se mueve", relative_folder, path.name)
        return None

    # si el destino es la propia carpeta donde ya esta el archivo, no hay
    # nada que hacer (y evita bucles de renombrado con la Patrulla Activa).
    if dest_dir.resolve() == path.parent.resolve():
        return None

    try:
        dest_dir.mkdir(parents=True, exist_ok=True)
        destination = _unique_destination(dest_dir, path.name)
        source_str = str(path)
        shutil.move(source_str, str(destination))
    except OSError as exc:
        logger.error("no se pudo mover %s: %s", path.name, exc)
        return None

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


def undo_move(move_id: int) -> tuple[dict | None, str | None]:
    """Devuelve un archivo del historial a su carpeta de origen.
    Retorna (info, None) si fue bien o (None, motivo) si no se pudo."""
    move = db.get_move(move_id)
    if move is None:
        return None, "movimiento no encontrado"
    if move.get("undone_at"):
        return None, "este movimiento ya se deshizo"

    current = Path(move["destination"])
    if not current.exists() or not current.is_file():
        return None, "el archivo ya no esta en su carpeta de destino"

    original_dir = Path(move["source"]).parent
    try:
        original_dir.mkdir(parents=True, exist_ok=True)
        restored = _unique_destination(original_dir, Path(move["source"]).name)
        shutil.move(str(current), str(restored))
    except OSError as exc:
        logger.error("no se pudo deshacer el movimiento %s: %s", move_id, exc)
        return None, "no se pudo mover el archivo de vuelta"

    db.mark_move_undone(move_id)
    return {
        "id": move_id,
        "filename": move["filename"],
        "restored_to": str(restored),
    }, None
