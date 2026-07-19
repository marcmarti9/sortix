"""Vigila la carpeta de Descargas en tiempo real y organiza cada archivo
nuevo en cuanto termina de descargarse. Esto es lo que enciende/apaga el
interruptor de 'Patrulla Activa' en la interfaz."""

import queue
import sys
import threading
import time
from pathlib import Path

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

from app.organizer import organize_file
from config.settings import IGNORED_SUFFIXES

# Limites de estabilidad para evitar organizar descargas incompletas.
STABLE_CHECKS_REQUIRED = 4
STABLE_CHECK_INTERVAL = 0.75
STABLE_WAIT_TIMEOUT_TICKS = 40  # ~30s de margen para descargas grandes


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
                    organize_file(path)
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
    """Arranca/para la vigilancia de una carpeta. Pensado como singleton
    dentro del proceso del servidor."""

    def __init__(self, directory: Path):
        self._directory = directory
        self._observer: Observer | None = None

    def start(self) -> None:
        if self.is_active():
            return
        self._directory.mkdir(parents=True, exist_ok=True)
        observer = Observer()
        observer.schedule(_DownloadEventHandler(), str(self._directory), recursive=False)
        observer.start()
        self._observer = observer

    def stop(self) -> None:
        if self._observer is not None:
            self._observer.stop()
            self._observer.join(timeout=5)
            self._observer = None

    def is_active(self) -> bool:
        return self._observer is not None and self._observer.is_alive()
