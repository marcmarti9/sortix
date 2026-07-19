"""Decide en que categoria (y, si coincide con alguno de tus Temas
personalizados: banco, gimnasio, una app concreta, lo que sea) cae un
archivo. Mira primero el nombre del archivo y, si hace falta, el contenido
(PDF / DOCX / TXT) buscando las palabras clave de cada Tema."""

import re
import unicodedata
import xml.etree.ElementTree as ET
import zipfile
import shutil
from pathlib import Path

from app import db, llm
from config.settings import load_categories

# Intentar importar dependencias de OCR (opcional)
try:
    import pytesseract
    from PIL import Image
    _OCR_AVAILABLE = shutil.which("tesseract") is not None
except ImportError:
    _OCR_AVAILABLE = False


MAX_CONTENT_CHARS = 20_000  # suficiente para detectar el tema sin leer el pdf entero
PDF_PAGES_TO_SCAN = 6
MIN_KEYWORD_HITS = 1

_categories = load_categories()

# extension -> nombre de categoria (p.ej. "pdf" -> "documents")
_EXT_TO_CATEGORY: dict[str, str] = {}
for _cat_name, _cat_data in _categories["categories"].items():
    for _ext in _cat_data["extensions"]:
        _EXT_TO_CATEGORY[_ext.lower()] = _cat_name

_CONTENT_EXTENSIONS = set(_categories["topic_matching"]["content_extensions"])
if _OCR_AVAILABLE:
    _CONTENT_EXTENSIONS.update({"png", "jpg", "jpeg", "tiff", "bmp", "gif"})


def normalize(text: str) -> str:
    """minusculas, sin tildes/diacriticos y con separadores (_, -, .) convertidos
    en espacios, para que "banco_extracto3" o "netflix-factura" tambien casen
    con la palabra clave suelta."""
    text = text.lower()
    text = unicodedata.normalize("NFKD", text)
    text = "".join(c for c in text if not unicodedata.combining(c))
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return text


def _extract_pdf_text(path: Path) -> str:
    try:
        from pypdf import PdfReader
    except ImportError:
        return ""
    try:
        reader = PdfReader(str(path))
    except Exception:
        return ""
    chunks = []
    for page in reader.pages[:PDF_PAGES_TO_SCAN]:
        try:
            chunks.append(page.extract_text() or "")
        except Exception:
            continue
        if sum(len(c) for c in chunks) >= MAX_CONTENT_CHARS:
            break
    return "".join(chunks)[:MAX_CONTENT_CHARS]


def _extract_docx_text(path: Path) -> str:
    try:
        with zipfile.ZipFile(path) as zf:
            with zf.open("word/document.xml") as f:
                xml_content = f.read(MAX_CONTENT_CHARS)
                # Prevencion de DoS / XML Entity Explosion (Billion Laughs / XXE):
                # un docx legitimo nunca contiene DTDs (<!DOCTYPE o <!ENTITY).
                if b"<!DOCTYPE" in xml_content or b"<!ENTITY" in xml_content:
                    return ""
                root = ET.fromstring(xml_content)
    except Exception:
        return ""
    ns = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
    texts = [node.text for node in root.iter("{%s}t" % ns["w"]) if node.text]
    return " ".join(texts)[:MAX_CONTENT_CHARS]


def _extract_txt_text(path: Path) -> str:
    try:
        with open(path, encoding="utf-8", errors="ignore") as f:
            return f.read(MAX_CONTENT_CHARS)
    except Exception:
        return ""


def _extract_image_text(path: Path) -> str:
    if not _OCR_AVAILABLE:
        return ""
    try:
        img = Image.open(path)
        text = pytesseract.image_to_string(img, timeout=10)
        return text[:MAX_CONTENT_CHARS]
    except Exception:
        return ""


def _extract_content(path: Path, ext: str) -> str:
    if ext == "pdf":
        return _extract_pdf_text(path)
    if ext == "docx":
        return _extract_docx_text(path)
    if ext == "txt":
        return _extract_txt_text(path)
    if ext in ("png", "jpg", "jpeg", "tiff", "bmp", "gif"):
        return _extract_image_text(path)
    return ""


def _count_keyword_hits(text_normalized: str, keywords: list[str]) -> int:
    hits = 0
    for kw in keywords:
        kw_norm = normalize(kw)
        if not kw_norm:
            continue
        pattern = r"\b" + re.escape(kw_norm) + r"\b"
        hits += len(re.findall(pattern, text_normalized))
    return hits


def _best_topic_for_text(text: str, topics: list[dict]) -> dict | None:
    if not text.strip():
        return None
    text_norm = normalize(text)
    best_topic = None
    best_hits = 0
    for topic in topics:
        hits = _count_keyword_hits(text_norm, topic["keywords"])
        if hits > best_hits:
            best_hits = hits
            best_topic = topic
    return best_topic if best_hits >= MIN_KEYWORD_HITS else None


def detect_topic(path: Path, ext: str, topics: list[dict]) -> dict | None:
    """Intenta identificar a que Tema pertenece un documento: primero por el
    nombre del archivo (rapido), y si no hay pista, por su contenido."""
    if not topics:
        return None

    topic = _best_topic_for_text(path.stem, topics)
    if topic:
        return topic

    if ext in _CONTENT_EXTENSIONS:
        content = _extract_content(path, ext)
        topic = _best_topic_for_text(content, topics)
        if topic:
            return topic

    return None


def _match_subcategory(category: str, stem: str) -> dict | None:
    """Subcategorias descriptivas por patrones en el nombre del archivo
    (capturas de pantalla, facturas, curriculums...)."""
    stem_norm = normalize(stem)
    for sub in _categories["categories"][category].get("subcategories", []):
        for pattern in sub.get("patterns", []):
            pattern_norm = normalize(pattern)
            if pattern_norm and re.search(r"\b" + re.escape(pattern_norm) + r"\b", stem_norm):
                return sub
    return None


def classify(path: Path) -> dict:
    """Devuelve {"category": str, "topic": str | None, "folder": str}
    donde 'folder' es la ruta relativa a la carpeta personal del usuario.

    Prioridad: Temas del usuario > subcategorias descriptivas por nombre >
    LLM local opcional (documentos) > carpeta base de la categoria."""
    ext = path.suffix.lower().lstrip(".")
    category = _EXT_TO_CATEGORY.get(ext, "other")

    content = ""
    if ext in _CONTENT_EXTENSIONS:
        topics = db.list_topics()
        if topics:
            topic = _best_topic_for_text(path.stem, topics)
            if topic is None:
                content = _extract_content(path, ext)
                topic = _best_topic_for_text(content, topics)
            if topic:
                return {"category": f"tema: {topic['name']}", "topic": topic["name"], "folder": topic["destination"], "rename_pattern": topic.get("rename_pattern")}

    sub = _match_subcategory(category, path.stem)
    if sub:
        return {"category": sub["label"], "topic": None, "folder": sub["folder"]}

    category_folder = _categories["categories"][category]["folder"]

    if ext in _CONTENT_EXTENSIONS and llm.LLM_ENABLED:
        if not content:
            content = _extract_content(path, ext)
        suggested = llm.suggest_subfolder(path.name, content, category_folder)
        if suggested:
            return {"category": f"IA local: {suggested.rsplit('/', 1)[-1]}", "topic": None, "folder": suggested}

    return {"category": category, "topic": None, "folder": category_folder}
