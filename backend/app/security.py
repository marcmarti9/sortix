"""Proteccion de la API y validacion de rutas de destino.

Sortix maneja documentos sensibles (extractos bancarios, facturas...), asi
que aunque solo escuche en localhost hay dos ataques realistas que cerrar:

- CSRF / DNS rebinding: una web abierta en tu navegador puede lanzar POSTs
  "a ciegas" contra 127.0.0.1 o resolver su dominio a tu IP local. Se
  bloquea comprobando las cabeceras Host y Origin de cada peticion.
- Path traversal: una regla o Tema con destino "../../x" o una ruta
  absoluta moveria archivos fuera de tu carpeta personal. Se bloquea
  normalizando y validando cada destino antes de guardarlo y de usarlo.
"""

import hmac
import re
from pathlib import Path, PurePosixPath, PureWindowsPath
from urllib.parse import urlsplit

from config.settings import API_TOKEN, HOME_DIR, HOST, PORT

# Nombres de host desde los que es legitimo hablar con Sortix cuando
# escucha solo en local.
_LOCAL_HOSTNAMES = {"127.0.0.1", "localhost", "[::1]", "::1"}

_EXTENSION_RE = re.compile(r"^[a-z0-9]{1,16}$")


# ---- validacion de destinos -------------------------------------------------

def clean_destination(raw: str) -> str | None:
    """Normaliza un destino escrito por el usuario a una ruta relativa
    segura dentro de su carpeta personal ("Documents/Banco"). Devuelve None
    si es invalido o intenta escaparse (absoluta, unidades de Windows, "..").
    """
    text = (raw or "").strip().replace("\\", "/")
    if not text:
        return None
    # rutas absolutas o con unidad de Windows ("C:...") no se admiten
    if PurePosixPath(text).is_absolute() or PureWindowsPath(text).is_absolute():
        return None
    if ":" in text or "\x00" in text:
        return None

    parts = [p.strip() for p in text.split("/")]
    parts = [p for p in parts if p and p != "."]
    if not parts or any(p == ".." for p in parts):
        return None

    cleaned = "/".join(parts)
    # comprobacion final contra la ruta real (cinturon y tirantes)
    resolved = (HOME_DIR / cleaned).resolve()
    home = HOME_DIR.resolve()
    if resolved != home and home not in resolved.parents:
        return None
    return cleaned


def safe_destination_dir(relative_folder: str) -> Path | None:
    """Convierte una carpeta relativa (ya guardada en la BD) en la ruta
    absoluta de destino, verificando otra vez que cae dentro de la carpeta
    personal. Ultima linea de defensa antes de mover nada."""
    cleaned = clean_destination(relative_folder)
    if cleaned is None:
        return None
    return HOME_DIR / cleaned


def valid_extension(raw: str) -> str | None:
    ext = (raw or "").strip().lower().lstrip(".")
    return ext if _EXTENSION_RE.fullmatch(ext) else None


# ---- proteccion de las peticiones HTTP -------------------------------------

def _hostname_of(value: str) -> str:
    """Extrae el hostname (sin puerto) de una cabecera Host u Origin."""
    if not value:
        return ""
    if "//" not in value:
        value = "//" + value
    try:
        return (urlsplit(value).hostname or "").lower()
    except ValueError:
        return ""


def _is_trusted_hostname(hostname: str) -> bool:
    if hostname in _LOCAL_HOSTNAMES:
        return True
    # si el usuario expone Sortix en su LAN (HOST=0.0.0.0 o una IP concreta),
    # acepta tambien el nombre/IP con el que llega, ya que en ese modo el
    # acceso esta protegido por el token obligatorio.
    return HOST not in ("127.0.0.1", "localhost", "::1") and bool(hostname)


def check_request(request) -> tuple[dict, int] | None:
    """Devuelve None si la peticion es legitima, o (payload, status) para
    rechazarla. Se aplica a todas las rutas (API y frontend)."""

    # 1) anti DNS-rebinding: la cabecera Host debe ser la esperada.
    if not _is_trusted_hostname(_hostname_of(request.host)):
        return {"error": "peticion rechazada: cabecera Host no reconocida"}, 403

    # 2) anti CSRF: en metodos que cambian estado, si el navegador envia
    #    Origin, este debe ser tambien local/confiable.
    if request.method not in ("GET", "HEAD", "OPTIONS"):
        origin = request.headers.get("Origin", "")
        if origin and origin != "null":
            if not _is_trusted_hostname(_hostname_of(origin)):
                return {"error": "peticion rechazada: origen no permitido"}, 403

    # 3) token compartido (obligatorio si Sortix no escucha solo en local).
    if API_TOKEN and request.path.startswith("/api/"):
        supplied = request.headers.get("X-Sortix-Token", "")
        if not hmac.compare_digest(supplied, API_TOKEN):
            return {"error": "token invalido o ausente"}, 401

    return None


def listening_beyond_localhost() -> bool:
    return HOST not in ("127.0.0.1", "localhost", "::1")


__all__ = [
    "API_TOKEN",
    "PORT",
    "check_request",
    "clean_destination",
    "listening_beyond_localhost",
    "safe_destination_dir",
    "valid_extension",
]
