# Sortix — Estado y Hoja de Ruta

> Documento vivo. Léelo entero antes de tocar el proyecto en una sesión nueva.
> Actualízalo cuando: cierres una funcionalidad, encuentres un bug relevante,
> tomes una decisión de producto, o se te ocurra algo a añadir al backlog.
> Formato de las entradas de historial: `AAAA-MM-DD — qué pasó`.

Última actualización: 2026-07-19.

---

## 1. Qué es Sortix

Organizador de archivos en tiempo real (Python/Flask + JS vanilla), enfocado
en Descargas. Vigila una carpeta, clasifica cada archivo nuevo por reglas,
palabras clave de contenido (con OCR opcional) o un LLM local, y lo mueve a
su sitio. 100% local: sin telemetría, sin llamadas a internet ni para la
IA. Repo público: https://github.com/marcmarti9/sortix (MIT).

---

## 2. Funcionalidades implementadas

### Motor de clasificación (cascada de prioridad, ver `backend/app/classifier.py` y `organizer.py`)
1. Reglas personalizadas con condiciones tipo bloques Scratch (nombre, extensión,
   tamaño, contenido; combinables con AND) — `condition-builder` en el frontend.
2. Temas por palabra clave: escanea nombre y contenido de PDF/DOCX/TXT, y OCR
   local (tesseract) en imágenes si está instalado.
3. Subcategorías por patrón en el nombre (capturas de pantalla, facturas, CVs...).
4. LLM local opcional (Ollama, `SORTIX_LLM=1`) para sugerir carpeta cuando nada
   más encaja. Apagado por defecto. Nunca sale de `127.0.0.1`.
5. Categoría base por extensión (fallback final).

### Automatización
- **Patrulla Activa**: watchdog en tiempo real, **solo sobre `DOWNLOADS_DIR`**,
  con detección de estabilidad (no toca `.crdownload`/`.part` a medias),
  pool de 4 hilos.
- Renombrado dinámico con placeholders (`{YYYY}`, `{MM}`, `{DD}`, `{Topic}`,
  `{Category}`, `{OriginalName}`, `{ext}`, y variantes `{FILE_*}` con la fecha
  del archivo).
- Mantenimiento / auto-trash: reglas de borrado por antigüedad, por carpeta,
  ejecutable manualmente desde la UI (`/api/maintenance/run`).
- Deduplicación por hash SHA256 (tamaño + hash exacto) dentro de Descargas +
  carpetas de categorías/temas, con limpieza desde la UI.
- Undo de un nivel desde el Historial.
- Simulación / dry-run (`/api/simulate`): previsualiza sin mover nada.
- Carpetas vigiladas extra (`/api/watched-folders`): se procesan **solo** al
  pulsar "Organizar ahora", NO en tiempo real (ver Gap #1 más abajo).
- Panel de estadísticas: total organizado, top categorías, actividad 30 días.

### Producto / distribución
- App de escritorio (`backend/desktop.py`): pywebview o navegador en modo `--app`.
- Instaladores de servicio en segundo plano: systemd (Linux), LaunchAgent (macOS),
  Task Scheduler (Windows), con sus `uninstall_*`.
- UI bilingüe ES/EN, tema claro/oscuro con View Transitions API.

### Seguridad (ver `backend/app/security.py`, `browser.py`)
- Anti path-traversal: todo destino se resuelve dentro de `HOME_DIR`.
- Anti CSRF / DNS-rebinding: comprobación de Host/Origin.
- Token de API opcional (`SORTIX_TOKEN`), obligatorio si se expone fuera de
  `127.0.0.1`.
- Cabeceras de privacidad (`no-store`, `nosniff`, `no-referrer`).
- Protección XML (Billion Laughs/XXE) al leer `.docx`.
- BD SQLite autorregenerable si se borra/corrompe en caliente (WAL).
- Guarda anti-bucle (no mueve un archivo a su propia carpeta actual).

### Tests
`backend/tests/test_all.py` — script único, **no usa pytest**, se ejecuta con:
```
cd backend && .venv/bin/python tests/test_all.py
```
21 bloques a fecha de este documento, todos en verde. Usa HOME y BD temporales,
no toca nada del usuario real.

---

## 3. Comparativa con la competencia

| | Sortix | Hazel (macOS) | DropIt (Win, gratis) | File Juggler (Win) |
|---|---|---|---|---|
| Multiplataforma | ✅ | ❌ solo Mac | ❌ solo Win | ❌ solo Win |
| Precio | Gratis/OSS | ~42$ | Gratis | ~25$ |
| Clasificación por contenido + OCR | ✅ | ❌ | ❌ | de pago |
| Varias carpetas vigiladas en tiempo real | ❌ (solo Descargas) | ✅ | ✅ | ✅ |
| Reglas por fecha/metadatos (EXIF...) | ❌ | ✅ | parcial | parcial |
| Extracción de comprimidos (.zip/.rar) | ❌ | ❌ | ✅ | ❌ |
| Clasificación con LLM local | ✅ (único en el sector) | ❌ | ❌ | ❌ |
| Deduplicación integrada | ✅ | ❌ | parcial | ❌ |
| Auto-trash por antigüedad | ✅ | ✅ | ❌ | ✅ |
| Programación por horario (cron) | ❌ | ✅ | ❌ | ✅ |

**Dónde ya ganamos**: gratis + multiplataforma + privacidad total (ni el
OCR ni el LLM salen de la máquina) + clasificación por contenido + LLM
local. Ninguna combina las cuatro cosas.

**Dónde estamos por detrás**: vigilancia real de varias carpetas, reglas
por fecha/metadatos, programación por horario, y el pulido de instalación
de un solo clic que sí tienen los competidores de pago.

---

## 4. Backlog priorizado

Marca `[x]` cuando esté commiteado y añade la fecha entre paréntesis.

### Impacto alto
- [ ] **Patrulla multi-carpeta real.** Las "carpetas vigiladas" son cosméticas:
      solo se procesan con "Organizar ahora", no hay watchdog en tiempo real.
      Extender `PatrolManager`/`_DownloadEventHandler` para vigilar una lista
      de directorios (Descargas + las vigiladas activas), no solo uno.
- [ ] **Programación (cron) para mantenimiento y carpetas vigiladas.** Ahora
      mismo todo es manual o al arrancar. Un scheduler simple (hilo con
      intervalo, o APScheduler) que dispare "Organizar ahora" y el
      mantenimiento a una hora fija.
- [ ] **Empaquetado de un clic.** Hoy requiere Python + venv manual; un build
      con PyInstaller/briefcase del modo escritorio bajaría mucho la barrera
      de entrada frente a instaladores de pago con DMG/EXE.

### Impacto medio
- [ ] **Condición de edad de archivo** en el condition-builder (reglas de
      clasificación, no solo mantenimiento) — el código de edad ya existe en
      `run_maintenance_cleanup`, falta exponerlo como campo `age_days` en
      `check_conditions`.
- [ ] **Extracción de comprimidos** (.zip/.rar) antes de clasificar el
      contenido interno — nadie en el sector lo hace, sería diferencial.
- [ ] **Deduplicación más rápida y con más alcance**: ahora SHA256 completo
      por candidato dentro de Descargas + carpetas de categorías/temas; no
      escala bien con colecciones grandes. Hash rápido (tamaño + primeros
      bytes) antes del SHA256 completo, y opción de escanear carpetas
      arbitrarias.

### Impacto bajo / nice-to-have
- [ ] **Notificaciones de escritorio** cuando la Patrulla mueve algo (hoy es
      silencioso).
- [ ] **Exportar/importar reglas como JSON** (plantillas compartibles tipo
      "estudiante", "freelance factura"...).
- [ ] **Aprender de correcciones**: si el usuario mueve a mano un archivo mal
      clasificado, ofrecer "¿creo una regla para esto?" — encaja con el LLM
      local ya existente.

---

## 5. Pendientes de gestión (no técnicos)
- [ ] Activar GitHub Sponsors / Ko-fi y descomentar `.github/FUNDING.yml`.
- [ ] `git push` de cualquier commit local que quede pendiente de subir.

---

## 6. Historial de sesiones

- **2026-07-19 (sesión 1)**: PR #1 de hardening + escritorio + LLM local
  mergeado. Repo hecho público.
- **2026-07-19 (sesión 2)**: revisión completa del código. Se encontraron y
  corrigieron desajustes de contrato frontend↔backend en simulación,
  carpetas vigiladas y estadísticas (commit `9327b68`, sin pushear aún).
  Añadidos tests de integración para esas 3 funcionalidades.
- **2026-07-19 (sesión 3)**: comparativa con la competencia (Hazel, DropIt,
  File Juggler) y creación de este documento (`ROADMAP.md`) para centralizar
  estado y backlog entre sesiones.
