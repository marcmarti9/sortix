# Sortix

**Privacy-first automatic download organizer.** Sortix watches your Downloads
folder and files everything where it belongs — bank statements, screenshots,
invoices, installers — into clearly named folders, entirely on your machine.

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org)
[![Platform](https://img.shields.io/badge/platform-Linux%20%7C%20Windows%20%7C%20macOS-lightgrey.svg)]()

## Why Sortix?

Your Downloads folder is where files go to die. Sortix gives every file a
proper home the moment it finishes downloading — and because it routinely
handles sensitive documents (bank statements, contracts, medical PDFs), it is
built local-first from the ground up:

- **100% local.** No cloud, no telemetry, no network calls. Content-based
  classification reads PDF/DOCX/TXT files on your machine and stores only
  the file name and where it was moved.
- **Descriptive folders**, not junk drawers: screenshots go to
  `Pictures/Capturas de pantalla`, invoices to `Documents/Facturas y recibos`,
  installers to `Downloads/Programas e instaladores`.
- **Topics**: teach Sortix your world once — "Bank" → `Documents/Banco` with
  keywords like `iban, extracto` — and every matching document (by file name
  *or* content) is filed there automatically, forever.
- **Undo anything** from the built-in history, collision-safe.
- **Hardened by default**: path-traversal-proof destinations, CSRF/DNS
  rebinding protection, token auth when exposed beyond localhost.

## Quick start

```bash
git clone https://github.com/marcmarti9/sortix
cd sortix/backend
python3 -m venv .venv
./.venv/bin/pip install -r requirements.txt
./.venv/bin/python main.py          # web UI at http://127.0.0.1:5000
```

### Desktop app mode

Run Sortix in its own window instead of a browser tab:

```bash
./.venv/bin/pip install -r requirements-desktop.txt   # optional, for a native window
./.venv/bin/python desktop.py
```

`desktop.py` uses a native window (pywebview) when available, falls back to a
Chromium app window (no address bar), and finally to your default browser. If
the background service is already running, it simply attaches to it.

### Run permanently in the background (recommended)

| OS | Install | Uninstall |
|---|---|---|
| Linux (systemd user service) | `cd backend/deploy && ./install_linux.sh` | `./uninstall_linux.sh` |
| Windows (Scheduled Task) | `powershell -ExecutionPolicy Bypass -File install_windows.ps1` | `...uninstall_windows.ps1` |
| macOS (LaunchDaemon) | `cd backend/deploy && ./install_macos.sh` | `./uninstall_macos.sh` |

On Linux, `sudo loginctl enable-linger $USER` keeps it running without an
open session. Once installed, open the UI whenever you want to toggle the
watcher ("Patrulla Activa"), manage Topics/rules, or undo a move.

## How files are classified

Priority order — first match wins:

1. **Your extension rules** (e.g. `.log` → `Documents/Logs`).
2. **Your Topics** — file name first, then document content (PDF/DOCX/TXT).
3. **Descriptive subcategories** by file-name patterns (screenshots,
   invoices, résumés, tickets, contracts…).
4. **Optional local LLM** (see below).
5. **Base category** by extension (images → `Pictures`, music → `Music`,
   archives → `Downloads/Archivos comprimidos`, unmatched documents →
   `Documents/Sin clasificar`, …).

All destinations are relative to your home folder and validated — a rule can
never move files outside it. Categories, folders and patterns are editable in
`backend/config/categories.json`; Topics and rules live in the UI.

## Optional: local AI folder naming

If your machine can handle it, Sortix can ask a small local LLM (via
[Ollama](https://ollama.com)) to name a folder for documents nothing else
matched — e.g. a random recipe PDF ends up in `Documents/Recetas` instead of
`Documents/Sin clasificar`. In `backend/.env`:

```ini
SORTIX_LLM=1
SORTIX_LLM_MODEL=llama3.2   # any small local model
```

Strictly off by default, and fully optional: on modest hardware just leave it
disabled — pattern-based classification handles everything. Document excerpts
are only ever sent to your own Ollama on localhost, never to the internet.
Suggested names are sanitized and confined to the category folder, and any
failure silently falls back to normal classification.

## Configuration

Copy `backend/.env.example` to `backend/.env`. Everything is optional:

| Variable | Default | Purpose |
|---|---|---|
| `HOST` / `PORT` | `127.0.0.1` / `5000` | Where the UI/API listens |
| `DOWNLOADS_DIR` | `~/Downloads` | Folder to watch |
| `SORTIX_TOKEN` | – | API token; **required** if `HOST` leaves localhost |
| `SORTIX_LLM` | off | Enable local LLM naming |
| `SORTIX_LLM_URL` / `SORTIX_LLM_MODEL` | Ollama defaults | Local model endpoint |

## Privacy & security

- Listens on `127.0.0.1` only by default, and additionally validates the
  `Host` and `Origin` headers of every request, so a malicious website open
  in your browser cannot talk to the API (CSRF / DNS rebinding).
- Rule/Topic destinations are validated as home-relative paths — absolute
  paths and `..` are rejected both when saved and again right before every
  move.
- Exposing Sortix on your network (`HOST=0.0.0.0`, e.g. a Raspberry Pi)
  requires `SORTIX_TOKEN`; without it the server refuses to start. Traffic
  is plain HTTP — use a trusted network or a TLS proxy.
- The SQLite database stores only your Topics, rules and the move history;
  it is git-ignored along with `.env`.
- API responses (which contain file names) are sent with `Cache-Control:
  no-store`.

## Testing

Self-contained integration suite — uses a temporary HOME and database, never
touches your real files:

```bash
cd backend
./.venv/bin/python tests/test_all.py
```

## Project structure

```
backend/    Python server (Flask + watchdog): watcher, classifier, API
frontend/   web UI (file-explorer style) for Topics, rules and history
database/   SQLite schema (Topics, rules, move history, settings)
```

## Contributing

Issues and pull requests are welcome — see [CONTRIBUTING.md](CONTRIBUTING.md).
The `main` branch is protected; all changes land via reviewed PRs.

## Support the project

If Sortix saves you time, you can support development through
**GitHub Sponsors** (button at the top of the repo). Thank you!

## License

[MIT](LICENSE) © Marc Martí Torralba
