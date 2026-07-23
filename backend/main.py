#!/usr/bin/env python3
"""Punto de entrada de Martix. Pensado tanto para ejecutarlo a mano como
para lanzarlo desde systemd (Linux) o el Programador de tareas (Windows)."""

import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from app import db
from app.server import create_app, resume_patrol_if_needed
from app.security import API_TOKEN, listening_beyond_localhost
from config.settings import HOST, PORT


def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    if listening_beyond_localhost() and not API_TOKEN:
        print(
            f"ERROR: HOST={HOST} expone Martix fuera de este equipo, y Martix\n"
            "maneja documentos personales. Define un token en backend/.env\n"
            "(MARTIX_TOKEN=una_clave_larga_y_aleatoria) o vuelve a HOST=127.0.0.1.",
            file=sys.stderr,
        )
        sys.exit(1)

    db.init_db()
    app = create_app()
    resume_patrol_if_needed()
    app.run(host=HOST, port=PORT, debug=False, threaded=True)


if __name__ == "__main__":
    main()
