#!/usr/bin/env python3
"""Script de empaquetado de Sortix para distribucion en 1-clic.

Utiliza PyInstaller para empaquetar la aplicacion de escritorio (desktop.py)
junto con la interfaz frontend y las configuraciones en un ejecutable.
"""

import os
import subprocess
import sys
from pathlib import Path


def build() -> None:
    backend_dir = Path(__file__).resolve().parent

    if sys.platform == "win32" or os.name == "nt":
        frontend_data = r"..\frontend;frontend"
        database_data = r"..\database;database"
        config_data = r"config;config"
    else:
        frontend_data = "../frontend:frontend"
        database_data = "../database:database"
        config_data = "config:config"

    desktop_script = backend_dir / "desktop.py"

    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--name=Sortix",
        "--onefile",
        "--add-data",
        frontend_data,
        "--add-data",
        database_data,
        "--add-data",
        config_data,
        "--clean",
        str(desktop_script),
    ]

    print("Iniciando empaquetado de Sortix...")
    print("Comando:", " ".join(cmd))

    result = subprocess.run(cmd, cwd=str(backend_dir))
    if result.returncode != 0:
        print(f"Error en la construccion con PyInstaller (codigo {result.returncode})", file=sys.stderr)
        sys.exit(result.returncode)

    dist_dir = backend_dir / "dist"
    print(f"\nEmpaquetado completado. El ejecutable esta disponible en: {dist_dir}")


if __name__ == "__main__":
    build()
