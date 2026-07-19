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
        if extension is None:
            return jsonify({"error": "extension invalida (solo letras y numeros, ej. pdf)"}), 400
        if destination is None:
            return jsonify({"error": "carpeta destino invalida: debe ser relativa a tu carpeta personal, ej. Documents/Facturas"}), 400
        rule = db.add_rule(extension, destination)
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

        topic = db.add_topic(name, destination, keywords)
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

    return app


def resume_patrol_if_needed() -> None:
    if db.get_setting("patrol_active", "0") == "1":
        patrol.start()
