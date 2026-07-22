#!/usr/bin/env python3
"""Sortix como app de escritorio nativa con bandeja del sistema (System Tray).

- Si el servidor de Sortix ya está corriendo (p.ej. como servicio), se conecta a él.
- Si no, lo arranca dentro de este mismo proceso.
- Utiliza PyQt6 con WebEngine y QSystemTrayIcon: al pulsar 'X' la ventana se oculta a la bandeja del sistema.
- Clic derecho en el icono de la bandeja: 'Abrir Sortix' o 'Salir de verdad'.
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
from app.security import API_TOKEN, listening_beyond_localhost
from app.server import create_app, resume_patrol_if_needed
from config.settings import HOST, PORT

URL = f"http://127.0.0.1:{PORT}"

WINDOW_TITLE = "Sortix — Intelligent File Organizer"
WINDOW_SIZE = (1120, 740)


def _port_open() -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.3)
        return s.connect_ex(("127.0.0.1", PORT)) == 0


def _start_server_in_background() -> None:
    if listening_beyond_localhost() and not API_TOKEN:
        print(
            f"ERROR: HOST={HOST} expone Sortix fuera de este equipo, y Sortix\n"
            "maneja documentos personales. Define un token en backend/.env\n"
            "(SORTIX_TOKEN=una_clave_larga_y_aleatoria) o vuelve a HOST=127.0.0.1.",
            file=sys.stderr,
        )
        sys.exit(1)

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
    print("ERROR: El servidor de Sortix no arrancó.", file=sys.stderr)
    sys.exit(1)


def _open_pyqt6_app() -> bool:
    """Abre Sortix en una ventana Qt6 nativa con icono en la bandeja del sistema (System Tray)."""
    try:
        from PyQt6.QtCore import QUrl, Qt
        from PyQt6.QtGui import QAction, QIcon, QPixmap, QPainter, QColor
        from PyQt6.QtWidgets import QApplication, QMainWindow, QMenu, QSystemTrayIcon
        from PyQt6.QtWebEngineWidgets import QWebEngineView
    except ImportError:
        return False

    app = QApplication.instance()
    if not app:
        app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)

    class SortixWindow(QMainWindow):
        def __init__(self):
            super().__init__()
            self.setWindowTitle(WINDOW_TITLE)
            self.resize(*WINDOW_SIZE)
            self.view = QWebEngineView(self)
            self.view.setUrl(QUrl(URL))
            self.setCentralWidget(self.view)

        def closeEvent(self, event):
            # En lugar de cerrar el proceso, ocultar a la bandeja del sistema
            event.ignore()
            self.hide()

    window = SortixWindow()

    # Dibujar icono elegante para la bandeja (Círculo índigo con S blanca)
    pixmap = QPixmap(32, 32)
    pixmap.fill(QColor(0, 0, 0, 0))
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    painter.setBrush(QColor(99, 102, 241)) # Indigo #6366f1
    painter.setPen(Qt.PenStyle.NoPen)
    painter.drawRoundedRect(2, 2, 28, 28, 8, 8)
    
    # Dibujar la 'S'
    painter.setPen(QColor(255, 255, 255))
    font = painter.font()
    font.setBold(True)
    font.setPixelSize(18)
    painter.setFont(font)
    painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, "S")
    painter.end()
    
    icon = QIcon(pixmap)
    window.setWindowIcon(icon)

    tray = QSystemTrayIcon(icon, app)
    tray.setToolTip("Sortix — Organizador en segundo plano")

    menu = QMenu()
    open_action = QAction("📂 Abrir Sortix", menu)
    open_action.triggered.connect(lambda: (window.show(), window.raise_(), window.activateWindow()))

    quit_action = QAction("❌ Salir de verdad", menu)
    quit_action.triggered.connect(lambda: (tray.hide(), app.quit()))

    menu.addAction(open_action)
    menu.addSeparator()
    menu.addAction(quit_action)

    tray.setContextMenu(menu)
    tray.activated.connect(lambda reason: (window.show(), window.raise_(), window.activateWindow()) if reason == QSystemTrayIcon.ActivationReason.Trigger else None)
    tray.show()

    window.show()
    app.exec()
    return True


def _open_pywebview() -> bool:
    try:
        import webview
    except ImportError:
        return False
    webview.create_window(WINDOW_TITLE, URL, width=WINDOW_SIZE[0], height=WINDOW_SIZE[1])
    webview.start()
    return True


def _open_browser_app_window() -> bool:
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

    if _open_pyqt6_app():
        return
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
