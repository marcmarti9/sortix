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
assert {"rules", "settings", "topics", "maintenance_rules"} <= tables, tables
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
    "Pictures/Screenshots/Screenshot 2026-07-19 at 10.00.00.png"), dests
assert "Documents/Invoices and receipts" in dests["factura_luz_enero.pdf"], dests
assert "Documents/Unclassified" in dests["notas sueltas.txt"], dests
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

# ---- renombrado dinamico, condiciones de reglas y acciones de duplicados ----
# 1) Prueba de renombrado dinamico & condiciones
r = client.post("/api/rules", json={
    "extension": "*",
    "destination": "Documents/CustomRules",
    "rename_pattern": "Custom-{OriginalName}-{YYYY}.{ext}",
    "conditions": [{"field": "name", "operator": "contains", "value": "remito"}]
})
assert r.status_code == 201, r.data

(downloads / "mi_remito_luz.pdf").write_bytes(b"%PDF-1.4 fake")
moved = organize_directory(downloads)
moved_remito = [m for m in moved if m["filename"] == "mi_remito_luz.pdf"]
assert len(moved_remito) == 1, moved
dest = Path(moved_remito[0]["destination"])
import datetime
current_year = datetime.datetime.now().strftime("%Y")
assert dest.name == f"Custom-mi_remito_luz-{current_year}.pdf", dest.name

# 2) Prueba de duplicados: accion "delete_source"
db.set_setting("duplicate_action", "delete_source")
(downloads / "mi_remito_luz.pdf").write_bytes(b"%PDF-1.4 fake") # crear duplicado exacto en Downloads
assert (downloads / "mi_remito_luz.pdf").exists()
moved = organize_directory(downloads)
moved_remito = [m for m in moved if m["filename"] == "mi_remito_luz.pdf"]
assert len(moved_remito) == 0, moved
assert not (downloads / "mi_remito_luz.pdf").exists() # se elimino el origen duplicado!

# 3) Prueba de duplicados: accion "skip"
db.set_setting("duplicate_action", "skip")
(downloads / "mi_remito_luz.pdf").write_bytes(b"%PDF-1.4 fake") # crear duplicado exacto
moved = organize_directory(downloads)
moved_remito = [m for m in moved if m["filename"] == "mi_remito_luz.pdf"]
assert len(moved_remito) == 0, moved
assert (downloads / "mi_remito_luz.pdf").exists() # se omitio, el archivo sigue ahi

# Limpieza
db.set_setting("duplicate_action", "suffix")
(downloads / "mi_remito_luz.pdf").unlink()
print("OK renombrado dinamico, condiciones y duplicados")

# ---- mantenimiento ----
assert len(db.list_maintenance_rules()) == 0
mr = db.add_maintenance_rule("Downloads", 5, 1)
assert mr["directory_path"] == "Downloads"
assert mr["max_age_days"] == 5
assert mr["active"] == 1
rules = db.list_maintenance_rules()
assert len(rules) == 1
assert rules[0]["directory_path"] == "Downloads"
db.delete_maintenance_rule(mr["id"])
assert len(db.list_maintenance_rules()) == 0
print("OK maintenance rules helpers (new schema)")

# GET rules initially empty
r = client.get("/api/maintenance/rules")
assert r.status_code == 200, r.data
assert r.get_json() == []

# POST rule with unsafe path should fail
r = client.post("/api/maintenance/rules", json={"directory_path": "../unsafe", "max_age_days": 10})
assert r.status_code == 400, r.status_code
r = client.post("/api/maintenance/rules", json={"directory_path": "/etc/passwd", "max_age_days": 10})
assert r.status_code == 400, r.status_code

# POST rule with invalid max_age_days should fail
r = client.post("/api/maintenance/rules", json={"directory_path": "Downloads", "max_age_days": -5})
assert r.status_code == 400, r.status_code
r = client.post("/api/maintenance/rules", json={"directory_path": "Downloads", "max_age_days": "abc"})
assert r.status_code == 400, r.status_code
r = client.post("/api/maintenance/rules", json={"directory_path": "Downloads"})
assert r.status_code == 400, r.status_code

# POST valid rule
r = client.post("/api/maintenance/rules", json={"directory_path": "Downloads", "max_age_days": 2, "active": True})
assert r.status_code == 201, r.data
rule = r.get_json()
assert rule["directory_path"] == "Downloads"
assert rule["max_age_days"] == 2
assert rule["active"] is True

# GET rules should contain our rule now
r = client.get("/api/maintenance/rules")
assert r.status_code == 200, r.data
rules_list = r.get_json()
assert len(rules_list) == 1
assert rules_list[0]["directory_path"] == "Downloads"
assert rules_list[0]["active"] is True

rule_id = rule["id"]

# Crear archivos de prueba de distintas edades
import time
maint_dir = downloads / "MaintTest"
maint_dir.mkdir(parents=True, exist_ok=True)

file1 = maint_dir / "keep_fresh.txt"
file2 = maint_dir / "keep_recent.txt"
file3 = maint_dir / "delete_old.txt"

file1.write_text("fresh")
file2.write_text("recent")
file3.write_text("old")

now = time.time()
os.utime(file1, (now, now))
os.utime(file2, (now - 1.1 * 86400, now - 1.1 * 86400))
os.utime(file3, (now - 3.1 * 86400, now - 3.1 * 86400))

# Ejecutar el mantenimiento
r = client.post("/api/maintenance/run")
assert r.status_code == 200, r.data
resp = r.get_json()
assert resp["success"] is True
assert resp["deleted"] == 1
assert resp["items"][0]["filename"] == "delete_old.txt"

# Verificar eliminaciones
assert file1.exists()
assert file2.exists()
assert not file3.exists()

# Verificar log de movimientos
moves = db.recent_moves(10)
maint_moves = [m for m in moves if m["category"] == "mantenimiento"]
assert len(maint_moves) == 1
assert maint_moves[0]["filename"] == "delete_old.txt"
assert maint_moves[0]["destination"] == "DELETED"

# Eliminar regla y limpiar
r = client.delete(f"/api/maintenance/rules/{rule_id}")
assert r.status_code == 204

if file1.exists():
    file1.unlink()
if file2.exists():
    file2.unlink()
if file3.exists():
    file3.unlink()
if maint_dir.exists():
    maint_dir.rmdir()

print("OK maintenance rules execution, path safety, and API")

# ---- pruebas de endpoints de duplicados ----
(downloads / "dup1.pdf").write_bytes(b"contenido_duplicado_123")
(downloads / "dup2.pdf").write_bytes(b"contenido_duplicado_123")
(downloads / "unico.pdf").write_bytes(b"contenido_unico_456")
(downloads / "diferente_mismo_tamano.pdf").write_bytes(b"diferente_mismo_tamanx")

try:
    r = client.get("/api/duplicates")
    assert r.status_code == 200
    dups = r.get_json()
    
    group = next((g for g in dups if g["size_bytes"] == 23), None)
    assert group is not None, dups
    
    files_in_group = [f["name"] for f in group["files"]]
    assert "dup1.pdf" in files_in_group
    assert "dup2.pdf" in files_in_group
    assert "unico.pdf" not in files_in_group
    assert "diferente_mismo_tamano.pdf" not in files_in_group
    
    r = client.post("/api/duplicates/clean", json=["../../etc/passwd"])
    assert r.status_code == 400
    
    dup1_entry = next(f for f in group["files"] if f["name"] == "dup1.pdf")
    dup1_rel_path = dup1_entry["path"]
    
    r = client.post("/api/duplicates/clean", json=[dup1_rel_path])
    assert r.status_code == 200
    assert r.get_json() == {"success": True, "deleted": 1}
    
    assert not (downloads / "dup1.pdf").exists()
    assert (downloads / "dup2.pdf").exists()

finally:
    for fn in ("dup1.pdf", "dup2.pdf", "unico.pdf", "diferente_mismo_tamano.pdf"):
        p = downloads / fn
        if p.exists():
            p.unlink()

print("OK endpoints de duplicados y limpieza")

print("\nTODAS LAS PRUEBAS PASARON")
