#!/usr/bin/env python3
"""Sortix como app de escritorio: abre la interfaz en una ventana propia en
vez de una pestana del navegador.

- Si el servidor de Sortix ya esta corriendo (p.ej. como servicio systemd),
  simplemente abre la ventana contra el.
- Si no, lo arranca dentro de este mismo proceso.
- La ventana usa pywebview si esta instalado (pip install pywebview); si no,
  recurre al modo app de Chrome/Chromium/Edge/Brave (ventana sin barra de
  navegador); y como ultimo recurso, el navegador por defecto.
"""

import logging
import shutil
import socket
import subprocess
import sys
import threading
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from app import db
from app.server import create_app, resume_patrol_if_needed
from config.settings import HOST, PORT

URL = f"http://127.0.0.1:{PORT}"

WINDOW_TITLE = "Sortix"
WINDOW_SIZE = (1100, 720)


def _port_open() -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.3)
        return s.connect_ex(("127.0.0.1", PORT)) == 0


def _start_server_in_background() -> None:
    db.init_db()
    app = create_app()
    resume_patrol_if_needed()
    thread = threading.Thread(
        target=lambda: app.run(host=HOST, port=PORT, debug=False, threaded=True),
        daemon=True,
    )
    thread.start()
    for _ in range(50):
        if _port_open():
            return
        time.sleep(0.1)
    print("ERROR: el servidor de Sortix no arranco.", file=sys.stderr)
    sys.exit(1)


def _open_pywebview() -> bool:
    try:
        import webview
    except ImportError:
        return False
    webview.create_window(WINDOW_TITLE, URL, width=WINDOW_SIZE[0], height=WINDOW_SIZE[1])
    webview.start()
    return True


def _open_browser_app_window() -> bool:
    """Ventana 'app' de un navegador Chromium: sin barra de direcciones,
    parece una aplicacion nativa y no requiere instalar nada."""
    candidates = [
        "chromium", "chromium-browser", "google-chrome", "google-chrome-stable",
        "brave-browser", "microsoft-edge", "msedge", "vivaldi",
    ]
    for name in candidates:
        binary = shutil.which(name)
        if binary:
            proc = subprocess.Popen(
                [binary, f"--app={URL}", f"--window-size={WINDOW_SIZE[0]},{WINDOW_SIZE[1]}"],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            )
            proc.wait()
            return True
    return False


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")

    started_here = False
    if not _port_open():
        _start_server_in_background()
        started_here = True

    if _open_pywebview():
        return
    if _open_browser_app_window():
        return

    import webbrowser
    webbrowser.open(URL)
    if started_here:
        print(f"Sortix corriendo en {URL} (Ctrl+C para salir).")
        try:
            while True:
                time.sleep(3600)
        except KeyboardInterrupt:
            pass


if __name__ == "__main__":
    main()
