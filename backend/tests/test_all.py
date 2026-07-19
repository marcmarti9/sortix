#!/usr/bin/env python3
"""Pruebas de integracion de Sortix. Autocontenidas: usan una carpeta
personal (HOME) y una base de datos temporales, sin tocar nada del usuario.

Ejecutar:  ./.venv/bin/python tests/test_all.py   (desde backend/)
"""

import os
import sqlite3
import sys
import tempfile
from pathlib import Path

# HOME falso ANTES de importar nada de Sortix (settings lee Path.home()
# en el momento del import).
_tmp = tempfile.mkdtemp(prefix="sortix-test-home-")
os.environ["HOME"] = _tmp
os.environ["USERPROFILE"] = _tmp  # equivalente en Windows

BACKEND = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BACKEND))

from config import settings  # noqa: E402

FAKE_HOME = Path(_tmp).resolve()
assert settings.HOME_DIR.resolve() == FAKE_HOME, settings.HOME_DIR
assert settings.DOWNLOADS_DIR == FAKE_HOME / "Downloads"

from app import db, security  # noqa: E402

# la BD tambien va a la carpeta temporal, no a database/sortix.db
db.DB_PATH = FAKE_HOME / "sortix-test.db"

from app.organizer import organize_directory  # noqa: E402

# ---- validacion de destinos ----
cd = security.clean_destination
assert cd("Documents/Banco") == "Documents/Banco"
assert cd("  Docs/./Sub//x  ") == "Docs/Sub/x"
assert cd("Docs\\Sub") == "Docs/Sub"
assert cd("../x") is None
assert cd("Docs/../../x") is None
assert cd("/etc/passwd") is None
assert cd("C:\\Windows") is None
assert cd("C:/Windows") is None
assert cd("") is None
assert cd("..") is None
print("OK validacion de destinos")

ve = security.valid_extension
assert ve("pdf") == "pdf"
assert ve(".PDF") == "pdf"
assert ve("p df") is None
assert ve("") is None
assert ve("pdf/../x") is None
print("OK validacion de extensiones")

# ---- migracion: BD antigua sin undone_at ni el resto de tablas ----
old = sqlite3.connect(db.DB_PATH)
old.execute("""CREATE TABLE moves_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT, filename TEXT NOT NULL,
    source TEXT NOT NULL, destination TEXT NOT NULL, category TEXT NOT NULL,
    moved_at TEXT NOT NULL DEFAULT (datetime('now')))""")
old.commit(); old.close()
db.init_db()
with db.get_conn() as conn:
    cols = {r["name"] for r in conn.execute("PRAGMA table_info(moves_log)")}
    tables = {r["name"] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
assert "undone_at" in cols, cols
assert {"rules", "settings", "topics"} <= tables, tables
print("OK migracion y regeneracion de esquema")

# ---- app y guardas HTTP ----
from app.server import create_app  # noqa: E402

app = create_app()
client = app.test_client()

r = client.get("/api/status")
assert r.status_code == 200, r.data
r = client.get("/api/status", headers={"Host": "evil.example.com"})
assert r.status_code == 403, (r.status_code, r.data)
r = client.post("/api/organize-now", headers={"Origin": "https://evil.example.com"})
assert r.status_code == 403, (r.status_code, r.data)
r = client.post("/api/organize-now", headers={"Origin": "http://127.0.0.1:5000"})
assert r.status_code == 200, (r.status_code, r.data)
print("OK guardas Host/Origin")

# ---- validacion en la API ----
r = client.post("/api/rules", json={"extension": "pdf", "destination": "../../etc"})
assert r.status_code == 400, (r.status_code, r.data)
r = client.post("/api/rules", json={"extension": "p!f", "destination": "Docs"})
assert r.status_code == 400
r = client.post("/api/topics", json={"name": "Banco", "destination": "/etc", "keywords": "banco"})
assert r.status_code == 400
r = client.post("/api/topics", json={"name": "Banco", "destination": "Documents/Banco", "keywords": "banco, extracto, iban"})
assert r.status_code == 201, r.data
print("OK validacion API")

# ---- organizar: imagen a Pictures/Descargas ----
downloads = settings.DOWNLOADS_DIR
downloads.mkdir(parents=True, exist_ok=True)
(downloads / "foto.jpg").write_bytes(b"x" * 10)
moved = organize_directory(downloads)
assert len(moved) == 1, moved
dest = Path(moved[0]["destination"])
assert dest == FAKE_HOME / "Pictures/foto.jpg", dest
assert dest.exists() and not (downloads / "foto.jpg").exists()

# ---- tema por nombre de archivo ----
(downloads / "extracto_enero.pdf").write_bytes(b"%PDF-1.4 fake")
moved = organize_directory(downloads)
assert len(moved) == 1 and "Banco" in moved[0]["destination"], moved
print("OK organizacion basica y por Tema")

# ---- subcategorias descriptivas por nombre ----
(downloads / "Screenshot 2026-07-19 at 10.00.00.png").write_bytes(b"png")
(downloads / "factura_luz_enero.pdf").write_bytes(b"%PDF-1.4 fake")
(downloads / "notas sueltas.txt").write_bytes(b"apuntes varios sin nada especial")
moved = organize_directory(downloads)
dests = {m["filename"]: m["destination"] for m in moved}
assert dests["Screenshot 2026-07-19 at 10.00.00.png"].endswith(
    "Pictures/Capturas de pantalla/Screenshot 2026-07-19 at 10.00.00.png"), dests
assert "Documents/Facturas y recibos" in dests["factura_luz_enero.pdf"], dests
assert "Documents/Sin clasificar" in dests["notas sueltas.txt"], dests
print("OK subcategorias descriptivas")

# ---- LLM local: apagado por defecto y sanitizacion estricta ----
from app import llm  # noqa: E402

assert llm.suggest_subfolder("x.pdf", "contenido", "Documents") is None  # desactivado
s = llm._sanitize_folder_name
assert s("Recetas") == "Recetas"
assert s('  "Apuntes de fisica".  ') == "Apuntes de fisica"
assert s("../etc") is None
assert s("a/b") is None
assert s("C:evil") is None
assert s("") is None
assert s("x" * 60) is None
print("OK LLM apagado por defecto y sanitizacion")

# ---- anti-bucle: regla con destino = Downloads ----
r = client.post("/api/rules", json={"extension": "zip", "destination": "Downloads"})
assert r.status_code == 201
(downloads / "cosa.zip").write_bytes(b"zip")
moved = organize_directory(downloads)
assert moved == [], moved
assert (downloads / "cosa.zip").exists()
print("OK guarda anti-bucle (destino == origen)")

# ---- destino corrupto en BD: no se mueve, no explota ----
with db.get_conn() as conn:
    conn.execute("UPDATE rules SET destination = '../../fuera' WHERE extension = 'zip'")
moved = organize_directory(downloads)
assert moved == [], moved
assert (downloads / "cosa.zip").exists()
assert not (FAKE_HOME.parent / "fuera").exists()
print("OK defensa en profundidad con BD corrupta")

# ---- undo via API ----
r = client.get("/api/log?limit=100")
log = r.get_json()
move = next(m for m in log if m["filename"] == "foto.jpg")
r = client.post(f"/api/log/{move['id']}/undo")
assert r.status_code == 200, r.data
assert (downloads / "foto.jpg").exists()
assert not (FAKE_HOME / "Pictures/foto.jpg").exists()
r = client.post(f"/api/log/{move['id']}/undo")
assert r.status_code == 409, (r.status_code, r.data)
r = client.post("/api/log/99999/undo")
assert r.status_code == 409
print("OK undo (y doble undo rechazado)")

# ---- undo cuando el archivo ya no esta ----
move2 = next(m for m in client.get("/api/log?limit=100").get_json() if m["filename"] == "extracto_enero.pdf")
Path(move2["destination"]).unlink()
r = client.post(f"/api/log/{move2['id']}/undo")
assert r.status_code == 409
print("OK undo con archivo desaparecido")

# ---- cabeceras de privacidad ----
r = client.get("/api/log")
assert r.headers.get("Cache-Control") == "no-store"
assert r.headers.get("X-Content-Type-Options") == "nosniff"
print("OK cabeceras de privacidad")

# ---- token ----
security.API_TOKEN = "secreto123"
try:
    r = client.get("/api/status")
    assert r.status_code == 401
    r = client.get("/api/status", headers={"X-Sortix-Token": "mal"})
    assert r.status_code == 401
    r = client.get("/api/status", headers={"X-Sortix-Token": "secreto123"})
    assert r.status_code == 200
    r = client.get("/")  # el frontend se sirve sin token (no expone datos)
    assert r.status_code == 200
finally:
    security.API_TOKEN = ""
print("OK token de API")

# ---- browse no permite escaparse ----
r = client.get("/api/browse?path=../../etc")
assert r.status_code == 400
r = client.get("/api/browse?path=/etc")
assert r.status_code == 400
r = client.get("/api/browse?path=Downloads")
assert r.status_code == 200
print("OK browse confinado a HOME")

print("\nTODAS LAS PRUEBAS PASARON")
