"""Servidor web de Sortix: sirve la interfaz (frontend/) y expone la API
que usa para controlar la Patrulla Activa, lanzar una organizacion manual,
gestionar reglas/Temas y deshacer movimientos del historial."""

import logging
from pathlib import Path
from urllib.parse import urlparse

from flask import Flask, jsonify, request, send_from_directory

from app import browser, db, security
from app.organizer import organize_directory, undo_move
from app.watcher import PatrolManager
from config.settings import DOWNLOADS_DIR, PROJECT_DIR, HOST, PORT

logger = logging.getLogger("sortix.server")

FRONTEND_DIR = PROJECT_DIR / "frontend"

patrol = PatrolManager(DOWNLOADS_DIR)


def _get_scan_dirs():
    dirs = set()
    dirs.add(DOWNLOADS_DIR.resolve())
    try:
        from config.settings import load_categories
        categories = load_categories()["categories"]
        for cat in categories.values():
            folder_str = cat.get("folder")
            if folder_str:
                from app.security import safe_destination_dir
                resolved = safe_destination_dir(folder_str)
                if resolved and resolved.exists():
                    dirs.add(resolved.resolve())
    except Exception:
        pass
    try:
        for topic in db.list_topics():
            folder_str = topic.get("destination")
            if folder_str:
                from app.security import safe_destination_dir
                resolved = safe_destination_dir(folder_str)
                if resolved and resolved.exists():
                    dirs.add(resolved.resolve())
    except Exception:
        pass
    return list(dirs)


def _find_all_files(scan_dirs):
    import os
    from config.settings import IGNORED_SUFFIXES
    files = []
    seen_paths = set()
    for root_dir in scan_dirs:
        if not root_dir.exists() or not root_dir.is_dir():
            continue
        for root, dirs, filenames in os.walk(root_dir):
            dirs[:] = [d for d in dirs if not d.startswith('.')]
            for f in filenames:
                if f.startswith('.'):
                    continue
                if Path(f).suffix.lower() in IGNORED_SUFFIXES:
                    continue
                file_path = Path(root) / f
                try:
                    resolved = file_path.resolve()
                    if resolved not in seen_paths and resolved.is_file():
                        seen_paths.add(resolved)
                        files.append(resolved)
                except OSError:
                    continue
    return files


def _scan_duplicates(files):
    from datetime import datetime
    from app.organizer import calculate_sha256
    from config.settings import HOME_DIR
    by_size = {}
    for path in files:
        try:
            size = path.stat().st_size
            by_size.setdefault(size, []).append(path)
        except OSError:
            continue
            
    duplicate_groups = {}
    for size, paths in by_size.items():
        if size == 0:
            continue
        if len(paths) < 2:
            continue
        for path in paths:
            sha = calculate_sha256(path)
            if sha:
                try:
                    rel_path = str(path.relative_to(HOME_DIR.resolve())).replace("\\", "/")
                except ValueError:
                    rel_path = str(path).replace("\\", "/")
                
                try:
                    stat = path.stat()
                    mtime_str = datetime.fromtimestamp(stat.st_mtime).isoformat(timespec="seconds")
                except OSError:
                    mtime_str = ""

                entry = {
                    "path": rel_path,
                    "name": path.name,
                    "mtime": mtime_str
                }
                duplicate_groups.setdefault(sha, {
                    "hash": sha,
                    "size_bytes": size,
                    "files": []
                })["files"].append(entry)

    result = [
        g for g in duplicate_groups.values()
        if len(g["files"]) >= 2
    ]
    
    for g in result:
        g["files"].sort(key=lambda x: x["path"])
        
    result.sort(key=lambda g: g["size_bytes"], reverse=True)
    return result


def create_app() -> Flask:
    app = Flask(__name__, static_folder=None)

    @app.before_request
    def guard_request():
        rejection = security.check_request(request)
        if rejection is not None:
            payload, status = rejection
            return jsonify(payload), status
        return None

    @app.after_request
    def privacy_headers(response):
        # las respuestas de la API contienen nombres y rutas de archivos
        # personales: que ni el navegador ni proxies las cacheen.
        if request.path.startswith("/api/"):
            response.headers["Cache-Control"] = "no-store"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Referrer-Policy"] = "no-referrer"
        return response

    @app.errorhandler(Exception)
    def handle_unexpected(exc):
        from werkzeug.exceptions import HTTPException
        if isinstance(exc, HTTPException):
            return exc
        logger.exception("error inesperado atendiendo %s", request.path)
        return jsonify({"error": "error interno de Sortix"}), 500

    @app.get("/")
    def index():
        return send_from_directory(FRONTEND_DIR, "index.html")

    @app.get("/<path:filename>")
    def frontend_assets(filename):
        return send_from_directory(FRONTEND_DIR, filename)

    @app.get("/api/status")
    def status():
        return jsonify({
            "active": patrol.is_active(),
            "files_organized": db.count_moves(),
            "downloads_dir": str(DOWNLOADS_DIR),
        })

    @app.post("/api/patrol/toggle")
    def toggle_patrol():
        payload = request.get_json(silent=True) or {}
        desired = payload.get("active")
        if desired is None:
            desired = not patrol.is_active()

        if desired:
            patrol.start()
        else:
            patrol.stop()

        db.set_setting("patrol_active", "1" if patrol.is_active() else "0")
        return jsonify({"active": patrol.is_active()})

    @app.post("/api/organize-now")
    def organize_now():
        moved = organize_directory(DOWNLOADS_DIR)
        return jsonify({"moved": len(moved), "items": moved})

    @app.get("/api/rules")
    def get_rules():
        return jsonify(db.list_rules())

    @app.post("/api/rules")
    def create_rule():
        payload = request.get_json(silent=True) or {}
        extension = security.valid_extension(payload.get("extension") or "")
        destination = security.clean_destination(payload.get("destination") or "")
        rename_pattern = (payload.get("rename_pattern") or "").strip() or None
        conditions = payload.get("conditions")
        if isinstance(conditions, (list, dict)):
            import json
            conditions = json.dumps(conditions)
        elif isinstance(conditions, str):
            conditions = conditions.strip() or None
        else:
            conditions = None

        if extension is None:
            return jsonify({"error": "extension invalida (solo letras y numeros, ej. pdf, o * para comodin)"}), 400
        if destination is None:
            return jsonify({"error": "carpeta destino invalida: debe ser relativa a tu carpeta personal, ej. Documents/Facturas"}), 400
        rule = db.add_rule(extension, destination, rename_pattern, conditions)
        return jsonify(rule), 201

    @app.delete("/api/rules/<int:rule_id>")
    def remove_rule(rule_id: int):
        db.delete_rule(rule_id)
        return "", 204

    @app.get("/api/log")
    def get_log():
        limit = request.args.get("limit", default=20, type=int)
        return jsonify(db.recent_moves(limit))

    @app.post("/api/log/<int:move_id>/undo")
    def undo_log_move(move_id: int):
        result, error = undo_move(move_id)
        if error:
            return jsonify({"error": error}), 409
        return jsonify(result)

    @app.get("/api/topics")
    def get_topics():
        return jsonify(db.list_topics())

    @app.post("/api/topics")
    def create_topic():
        payload = request.get_json(silent=True) or {}
        name = (payload.get("name") or "").strip()
        destination = security.clean_destination(payload.get("destination") or "")
        keywords = payload.get("keywords") or []
        rename_pattern = (payload.get("rename_pattern") or "").strip() or None
        if isinstance(keywords, str):
            keywords = [k.strip() for k in keywords.split(",")]
        keywords = [k for k in keywords if k]

        if not name or len(name) > 80:
            return jsonify({"error": "el nombre del tema es obligatorio (max. 80 caracteres)"}), 400
        if destination is None:
            return jsonify({"error": "carpeta destino invalida: debe ser relativa a tu carpeta personal, ej. Documents/Banco"}), 400
        if not keywords:
            return jsonify({"error": "indica al menos una palabra clave"}), 400

        # Validacion de Path Traversal / Seguridad
        if browser.resolve_safe_path(destination) is None:
            return jsonify({"error": "Ruta de destino no permitida o insegura"}), 400

        topic = db.add_topic(name, destination, keywords, rename_pattern)
        return jsonify(topic), 201

    @app.delete("/api/topics/<int:topic_id>")
    def remove_topic(topic_id: int):
        db.delete_topic(topic_id)
        return "", 204

    @app.get("/api/tree")
    def get_tree():
        return jsonify(browser.build_tree())

    @app.get("/api/browse")
    def browse_folder():
        raw_path = request.args.get("path", "")
        resolved = browser.resolve_safe_path(raw_path)
        if resolved is None:
            return jsonify({"error": "ruta no permitida"}), 400
        if not resolved.exists():
            return jsonify({"path": raw_path, "exists": False, "entries": []})
        if not resolved.is_dir():
            return jsonify({"error": "la ruta no es una carpeta"}), 400
        return jsonify({
            "path": raw_path,
            "exists": True,
            "entries": browser.list_directory(resolved),
        })

    @app.get("/api/settings")
    def get_settings():
        return jsonify({
            "duplicate_action": db.get_setting("duplicate_action", "suffix"),
        })

    @app.post("/api/settings")
    def update_settings():
        payload = request.get_json(silent=True) or {}
        if "duplicate_action" in payload:
            action = payload["duplicate_action"]
            if action in ("suffix", "skip", "delete_source"):
                db.set_setting("duplicate_action", action)
        return jsonify({
            "duplicate_action": db.get_setting("duplicate_action", "suffix")
        })

    @app.get("/api/duplicates")
    def get_duplicates():
        scan_dirs = _get_scan_dirs()
        all_files = _find_all_files(scan_dirs)
        duplicates = _scan_duplicates(all_files)
        return jsonify(duplicates)

    @app.post("/api/duplicates/clean")
    def clean_duplicates():
        payload = request.get_json(silent=True)
        if isinstance(payload, dict):
            files_to_delete = payload.get("files") or []
        elif isinstance(payload, list):
            files_to_delete = payload
        else:
            files_to_delete = []

        resolved_paths = []
        for f_path in files_to_delete:
            resolved = browser.resolve_safe_path(f_path)
            if resolved is None:
                return jsonify({"error": f"ruta no permitida: {f_path}"}), 400
            
            if resolved.exists():
                if not resolved.is_file():
                    return jsonify({"error": f"la ruta no es un archivo: {f_path}"}), 400
                resolved_paths.append(resolved)

        deleted_count = 0
        for resolved_path in resolved_paths:
            try:
                resolved_path.unlink()
                deleted_count += 1
            except OSError as e:
                logger.exception("Error unlinking file %s", resolved_path)
                return jsonify({"error": f"no se pudo eliminar: {resolved_path.name}"}), 500
        
        return jsonify({"success": True, "deleted": deleted_count})

    return app


def resume_patrol_if_needed() -> None:
    if db.get_setting("patrol_active", "0") == "1":
        patrol.start()
