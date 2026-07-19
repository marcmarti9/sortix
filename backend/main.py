#!/usr/bin/env python3
"""Punto de entrada de Sortix. Pensado tanto para ejecutarlo a mano como
para lanzarlo desde systemd (Linux) o el Programador de tareas (Windows)."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from app import db
from app.server import create_app, resume_patrol_if_needed
from config.settings import HOST, PORT


def main() -> None:
    db.init_db()
    app = create_app()
    resume_patrol_if_needed()
    app.run(host=HOST, port=PORT, debug=False, threaded=True)


if __name__ == "__main__":
    main()
