"""Vigila la carpeta de Descargas en tiempo real y organiza cada archivo
nuevo en cuanto termina de descargarse. Esto es lo que enciende/apaga el
interruptor de 'Patrulla Activa' en la interfaz."""

import queue
import subprocess
import sys
import threading
import time
from pathlib import Path

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

from app.organizer import organize_file
from config.settings import DOWNLOADS_DIR, IGNORED_SUFFIXES

# Limites de estabilidad para evitar organizar descargas incompletas.
STABLE_CHECKS_REQUIRED = 4
STABLE_CHECK_INTERVAL = 0.75
STABLE_WAIT_TIMEOUT_TICKS = 40  # ~30s de margen para descargas grandes


def send_notification(title: str, message: str) -> None:
    """Envía una notificación nativa del sistema operativo de forma no bloqueante.

    El título y el mensaje pueden contener nombres de archivo controlados por el
    usuario (o por quien le envíe una descarga), así que nunca se interpolan
    directamente en un script de AppleScript/PowerShell: se pasan como
    argumentos separados para evitar inyección de comandos.
    """
    def _notify():
        try:
            if sys.platform.startswith("linux"):
                subprocess.Popen(["notify-send", title, message])
            elif sys.platform == "darwin":
                script = (
                    "on run argv\n"
                    "  display notification (item 2 of argv) with title (item 1 of argv)\n"
                    "end run"
                )
                subprocess.Popen(["osascript", "-e", script, title, message])
            elif sys.platform == "win32":
                ps_script = (
                    "param([string]$Title, [string]$Message) "
                    "Add-Type -AssemblyName System.Windows.Forms; "
                    "[System.Windows.Forms.MessageBox]::Show($Message, $Title) | Out-Null"
                )
                subprocess.Popen(
                    ["powershell", "-NoProfile", "-Command", ps_script, "-Title", title, "-Message", message]
                )
        except Exception:
            pass

    threading.Thread(target=_notify, daemon=True).start()


class _DownloadEventHandler(FileSystemEventHandler):
    def __init__(self):
        super().__init__()
        self._in_progress: set[Path] = set()
        self._lock = threading.Lock()
        
        # Sistema de cola para limitar la concurrencia a exactamente 4 hilos demonio,
        # previniendo la caida del sistema por explosion de hilos (DoS).
        self._queue = queue.Queue()
        for _ in range(4):
            threading.Thread(target=self._worker, daemon=True).start()

    def on_created(self, event):
        if not event.is_directory:
            self._schedule(Path(event.src_path))

    def on_moved(self, event):
        # los navegadores suelen descargar a "archivo.crdownload" y luego
        # renombrar a "archivo.pdf" al terminar: eso dispara on_moved.
        if not event.is_directory and event.dest_path:
            self._schedule(Path(event.dest_path))

    def _schedule(self, path: Path):
        if path.suffix.lower() in IGNORED_SUFFIXES:
            return
        with self._lock:
            if path in self._in_progress:
                return
            self._in_progress.add(path)
        self._queue.put(path)

    def _worker(self):
        while True:
            path = self._queue.get()
            try:
                if self._wait_until_stable(path):
                    result = organize_file(path)
                    if result:
                        filename = result.get("filename", path.name)
                        category = result.get("category", "")
                        msg = f"Archivo organizado: {filename} ({category})" if category else f"Archivo organizado: {filename}"
                        send_notification("Sortix", msg)
            except Exception as e:
                # Evita que el hilo muera de forma silenciosa e informa del fallo en stderr.
                print(f"[Sortix Watcher Error] No se pudo organizar {path.name}: {e}", file=sys.stderr)
            finally:
                with self._lock:
                    self._in_progress.discard(path)
                self._queue.task_done()

    @staticmethod
    def _wait_until_stable(path: Path) -> bool:
        last_size = -1
        stable_count = 0
        for _ in range(STABLE_WAIT_TIMEOUT_TICKS):
            if not path.exists():
                return False
            try:
                size = path.stat().st_size
            except OSError:
                # En Windows, los archivos abiertos/descargando pueden lanzar violacion de acceso (OSError).
                # Reiniciamos la cuenta de estabilidad y esperamos al siguiente tick en lugar de abortar.
                stable_count = 0
                time.sleep(STABLE_CHECK_INTERVAL)
                continue
            if size == last_size and size > 0:
                stable_count += 1
                if stable_count >= STABLE_CHECKS_REQUIRED:
                    return True
            else:
                stable_count = 0
                last_size = size
            time.sleep(STABLE_CHECK_INTERVAL)
        return False


class PatrolManager:
    """Arranca/para la vigilancia de múltiples carpetas en tiempo real. Pensado como singleton
    dentro del proceso del servidor."""

    def __init__(self, directory: Path | None = None, directories: list[Path] | None = None):
        if directories is not None:
            self._base_directories = [Path(d) for d in directories]
        elif directory is not None:
            self._base_directories = [Path(directory)]
        else:
            self._base_directories = [DOWNLOADS_DIR]

        self._observer: Observer | None = None
        self._watches: dict[Path, object] = {}
        self._lock = threading.Lock()
        self._handler = _DownloadEventHandler()

    def get_watched_directories(self) -> list[Path]:
        with self._lock:
            return list(self._watches.keys())

    def _get_target_directories(self) -> list[Path]:
        dirs = set()
        for base in self._base_directories:
            try:
                base.mkdir(parents=True, exist_ok=True)
                dirs.add(base.resolve())
            except OSError:
                pass

        try:
            from app import db, browser
            for wf in db.list_watched_folders():
                if wf.get("active", 1):
                    folder_path_str = wf.get("folder_path", "")
                    if folder_path_str:
                        resolved = browser.resolve_safe_path(folder_path_str)
                        if resolved:
                            try:
                                resolved.mkdir(parents=True, exist_ok=True)
                                dirs.add(resolved.resolve())
                            except OSError:
                                pass
        except Exception as e:
            print(f"[Sortix Watcher Warning] Error obteniendo carpetas vigiladas de BD: {e}", file=sys.stderr)

        return list(dirs)

    def _update_watches_locked(self) -> None:
        if self._observer is None or not self._observer.is_alive():
            return

        target_dirs = set(self._get_target_directories())
        current_dirs = set(self._watches.keys())

        # Cancelar vigilancia de carpetas eliminadas
        for d in current_dirs - target_dirs:
            watch = self._watches.pop(d)
            try:
                self._observer.unschedule(watch)
            except Exception as e:
                print(f"[Sortix Watcher Warning] No se pudo des-vigilar {d}: {e}", file=sys.stderr)

        # Iniciar vigilancia de nuevas carpetas
        for d in target_dirs - current_dirs:
            try:
                d.mkdir(parents=True, exist_ok=True)
                watch = self._observer.schedule(self._handler, str(d), recursive=False)
                self._watches[d] = watch
            except Exception as e:
                print(f"[Sortix Watcher Error] No se pudo vigilar {d}: {e}", file=sys.stderr)

    def start(self) -> None:
        with self._lock:
            if self.is_active():
                self._update_watches_locked()
                return
            observer = Observer()
            observer.start()
            self._observer = observer
            self._watches.clear()
            self._update_watches_locked()

    def stop(self) -> None:
        with self._lock:
            if self._observer is not None:
                try:
                    self._observer.stop()
                    self._observer.join(timeout=5)
                except Exception:
                    pass
                self._observer = None
                self._watches.clear()

    def update_watched_folders(self) -> None:
        with self._lock:
            if self.is_active():
                self._update_watches_locked()

    def is_active(self) -> bool:
        return self._observer is not None and self._observer.is_alive()

