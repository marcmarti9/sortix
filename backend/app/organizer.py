"""Decide el destino final de un archivo (reglas del usuario primero, si no
el clasificador inteligente), lo mueve de forma segura sin pisar archivos
con el mismo nombre, y permite deshacer un movimiento del historial."""

import datetime
import hashlib
import json
import logging
import re
import shutil
from pathlib import Path

from app import db
from app.classifier import classify, normalize, _extract_content
from app.security import safe_destination_dir
from config.settings import HOME_DIR, IGNORED_SUFFIXES

logger = logging.getLogger("sortix.organizer")


def calculate_sha256(path: Path) -> str:
    h = hashlib.sha256()
    try:
        with open(path, "rb") as f:
            while chunk := f.read(8192):
                h.update(chunk)
    except OSError:
        pass
    return h.hexdigest()


def check_conditions(path: Path, ext: str, conditions_str: str | None) -> bool:
    if not conditions_str:
        return True # Si no hay condiciones adicionales, es un match directo
    try:
        conditions = json.loads(conditions_str)
    except Exception:
        return False
    if not isinstance(conditions, list):
        return False

    for cond in conditions:
        field = cond.get("field")
        op = cond.get("operator")
        val = cond.get("value")
        if not field or not op:
            continue

        actual = None
        if field == "name":
            actual = path.name
        elif field == "stem":
            actual = path.stem
        elif field == "extension":
            actual = ext
        elif field == "size_kb":
            try:
                actual = path.stat().st_size / 1024
            except OSError:
                return False
        elif field == "content":
            actual = _extract_content(path, ext)

        if actual is None:
            return False

        if op == "contains":
            if not isinstance(actual, str) or normalize(val) not in normalize(actual):
                return False
        elif op == "not_contains":
            if not isinstance(actual, str) or normalize(val) in normalize(actual):
                return False
        elif op == "equals":
            if normalize(str(actual)) != normalize(str(val)):
                return False
        elif op == "starts_with":
            if not isinstance(actual, str) or not normalize(actual).startswith(normalize(val)):
                return False
        elif op == "ends_with":
            if not isinstance(actual, str) or not normalize(actual).endswith(normalize(val)):
                return False
        elif op == "gt":
            try:
                if float(actual) <= float(val):
                    return False
            except ValueError:
                return False
        elif op == "lt":
            try:
                if float(actual) >= float(val):
                    return False
            except ValueError:
                return False
    return True


def format_rename_pattern(pattern: str, path: Path, category: str, topic_name: str | None) -> str:
    now = datetime.datetime.now()
    try:
        mtime = datetime.datetime.fromtimestamp(path.stat().st_mtime)
    except OSError:
        mtime = now

    placeholders = {
        "{YYYY}": now.strftime("%Y"),
        "{MM}": now.strftime("%m"),
        "{DD}": now.strftime("%d"),
        "{FILE_YYYY}": mtime.strftime("%Y"),
        "{FILE_MM}": mtime.strftime("%m"),
        "{FILE_DD}": mtime.strftime("%d"),
        "{OriginalName}": path.stem,
        "{Topic}": topic_name or "",
        "{Category}": category,
        "{ext}": path.suffix.lower().lstrip("."),
    }

    new_name = pattern
    for placeholder, val in placeholders.items():
        new_name = new_name.replace(placeholder, val)

    # Si el patron no especifica la extension y el archivo original tiene una, se la anadimos
    if not Path(new_name).suffix and path.suffix:
        new_name += path.suffix

    # Sanitizar el nombre del archivo final
    new_name = re.sub(r'[\x00/\\:*?"<>|]', '_', new_name)
    return new_name


def resolve_destination_folder(path: Path) -> tuple[str, str, str | None]:
    """Devuelve (categoria, carpeta_relativa_a_home, rename_pattern) para un archivo dado."""
    ext = path.suffix.lower().lstrip(".")

    # Buscar en todas las reglas personalizadas (incluyendo condicionales)
    rules = db.list_rules()
    for rule in rules:
        rule_ext = rule.get("extension")
        # Si la regla especifica una extension concreta (y no es wildcard *), debe coincidir
        if rule_ext and rule_ext != "*" and rule_ext != ext:
            continue
        # Comprobar condiciones (AND)
        if check_conditions(path, ext, rule.get("conditions")):
            return "regla personalizada", rule["destination"], rule.get("rename_pattern")

    # Clasificar con el categorizador inteligente
    result = classify(path)
    return result["category"], result["folder"], result.get("rename_pattern")


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

    category, relative_folder, rename_pattern = resolve_destination_folder(path)

    dest_dir = safe_destination_dir(relative_folder)
    if dest_dir is None:
        logger.warning("destino invalido %r para %s; no se mueve", relative_folder, path.name)
        return None

    # si el destino es la propia carpeta donde ya esta el archivo, no hay
    # nada que hacer (y evita bucles de renombrado con la Patrulla Activa).
    if dest_dir.resolve() == path.parent.resolve():
        return None

    # Determinar nombre de archivo destino
    topic_name = category.split(": ", 1)[1] if category.startswith("tema: ") else None
    if rename_pattern:
        dest_filename = format_rename_pattern(rename_pattern, path, category, topic_name)
    else:
        dest_filename = path.name

    # Control de duplicaciones si ya existe el nombre
    destination = dest_dir / dest_filename
    if destination.exists():
        # Comprobar si son exactamente identicos (tamaño y hash SHA256)
        if destination.stat().st_size == path.stat().st_size and calculate_sha256(destination) == calculate_sha256(path):
            action = db.get_setting("duplicate_action", "suffix")
            if action == "delete_source":
                try:
                    path.unlink()
                    logger.info("Eliminado duplicado en origen: %s (ya existe identico en destino)", path.name)
                except OSError as exc:
                    logger.error("error eliminando duplicado %s: %s", path.name, exc)
                return None
            elif action == "skip":
                logger.info("Omitido movimiento: %s ya existe e identico en destino", path.name)
                return None
        
        # Si no son identicos (o la opcion es suffix), generamos un nombre unico
        destination = _unique_destination(dest_dir, dest_filename)

    # Si el destino es la propia carpeta donde ya esta el archivo Y tiene el mismo nombre, no hay
    # nada que hacer (y evita bucles de renombrado con la Patrulla Activa).
    if destination.resolve() == path.resolve():
        return None

    try:
        dest_dir.mkdir(parents=True, exist_ok=True)
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
    Retorna (datos_movimiento, mensaje_error)."""
    move = db.get_move(move_id)
    if not move:
        return None, "movimiento no encontrado en la base de datos"
    if move["undone_at"]:
        return None, "este movimiento ya fue deshecho anteriormente"

    dest_path = Path(move["destination"])
    orig_path = Path(move["source"])

    if not dest_path.exists():
        return None, f"el archivo ya no esta en su carpeta de destino ({dest_path.name})"

    orig_dir = orig_path.parent
    try:
        orig_dir.mkdir(parents=True, exist_ok=True)
        final_orig = _unique_destination(orig_dir, orig_path.name)
        shutil.move(str(dest_path), str(final_orig))
    except OSError as exc:
        logger.error("fallo al deshacer el movimiento de %s: %s", dest_path.name, exc)
        return None, f"error del sistema de archivos: {exc}"

    db.mark_move_undone(move_id)
    return {
        "filename": dest_path.name,
        "source": move["destination"],
        "destination": str(final_orig),
    }, None
