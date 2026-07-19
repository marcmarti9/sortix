"""Nombrado opcional de carpetas con un LLM 100% local (Ollama).

Apagado por defecto: solo se activa con SORTIX_LLM=1 en .env, pensado para
equipos con recursos de sobra. Cuando un documento no encaja en ningun Tema
ni subcategoria, se le pide a un modelo local (via http://127.0.0.1:11434)
un nombre corto de carpeta y el archivo se guarda en
"<carpeta de la categoria>/<ese nombre>".

Privacidad: el fragmento de texto del documento solo viaja a tu propio
Ollama en localhost, nunca a internet. Y ante cualquier fallo (Ollama
apagado, timeout, respuesta rara) se vuelve en silencio a la clasificacion
normal, asi que un PC modesto sin Ollama no nota nada.
"""

import json
import logging
import re
import urllib.request

from config.settings import LLM_ENABLED, LLM_MODEL, LLM_URL

logger = logging.getLogger("sortix.llm")

MAX_EXCERPT_CHARS = 1200
TIMEOUT_SECONDS = 25

# nombre de carpeta valido: 2-32 caracteres, letras/numeros/espacios/guiones.
_NAME_RE = re.compile(r"^[0-9A-Za-zÁÉÍÓÚÜÑáéíóúüñ][0-9A-Za-zÁÉÍÓÚÜÑáéíóúüñ \-]{1,31}$")

_PROMPT = (
    "Eres un archivador de documentos. Te doy el nombre de un archivo y un "
    "fragmento de su contenido. Responde SOLO con un nombre de carpeta corto "
    "y descriptivo en espanol (1 a 3 palabras, sin barras, sin comillas, sin "
    "punto final) donde guardarias este documento. Ejemplos de respuesta: "
    "Recetas, Apuntes de fisica, Seguro del coche.\n\n"
    "Archivo: {filename}\n"
    "Contenido:\n{excerpt}\n\n"
    "Carpeta:"
)


def _sanitize_folder_name(raw: str) -> str | None:
    text = (raw or "").strip().splitlines()[0] if (raw or "").strip() else ""
    text = text.strip("\"'` .")
    if "/" in text or "\\" in text or ".." in text or ":" in text:
        return None
    return text if _NAME_RE.fullmatch(text) else None


def suggest_subfolder(filename: str, content_excerpt: str, category_folder: str) -> str | None:
    """Devuelve una carpeta relativa "categoria/Nombre sugerido" o None si el
    LLM esta desactivado, no responde o la respuesta no es un nombre valido."""
    if not LLM_ENABLED:
        return None

    prompt = _PROMPT.format(
        filename=filename,
        excerpt=(content_excerpt or "")[:MAX_EXCERPT_CHARS],
    )
    payload = json.dumps({
        "model": LLM_MODEL,
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": 0, "num_predict": 12},
    }).encode("utf-8")

    try:
        req = urllib.request.Request(
            LLM_URL.rstrip("/") + "/api/generate",
            data=payload,
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=TIMEOUT_SECONDS) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except Exception as exc:
        logger.warning("LLM local no disponible (%s); clasificacion normal", exc)
        return None

    name = _sanitize_folder_name(data.get("response", ""))
    if name is None:
        logger.info("respuesta del LLM descartada por no ser un nombre valido")
        return None
    return f"{category_folder}/{name}"
