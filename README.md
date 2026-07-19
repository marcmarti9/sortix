<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python&logoColor=white" alt="Python Version" />
  <img src="https://img.shields.io/badge/Flask-3.0%2B-black?style=for-the-badge&logo=flask&logoColor=white" alt="Flask" />
  <img src="https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey?style=for-the-badge" alt="Platforms" />
  <img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge" alt="License" />
</p>

<h1 align="center">Sortix</h1>
<p align="center"><strong>An intelligent, real-time downloads organizer and local file explorer.</strong></p>
<p align="center">Sortix runs silently in the background, monitors your Downloads directory, and automatically organizes incoming files into target folders based on file types, extension rules, or content-matching keywords.</p>

---

## Why Sortix?

Your Downloads folder is where files go to die. Sortix gives every file a proper home the moment it finishes downloading — and because it routinely handles sensitive documents (bank statements, contracts, invoices, medical PDFs), it is built privacy-first from the ground up:

* **100% Local:** No cloud, no telemetry, no network calls. Content-based classification scans PDF/DOCX/TXT files on your machine.
* **Security Headers & Controls:** API responses contain sensitive names and paths, so they are protected with strictly configured headers (`Cache-Control: no-store`, `X-Content-Type-Options: nosniff`, `Referrer-Policy: no-referrer`).
* **Path Traversal Protection:** All rules and custom topics are sanitized to ensure destination directories remain strictly within your personal home directory (~).
* **Anti-Loop Guards:** Defensive checks ensure the destination folder does not loop back into the watched downloads directory, avoiding endless watchdogs events.

---

## Features

* **Active Patrol (Real-time monitoring):** Instantly detects new files landing in your Downloads directory and schedules organization once download completes (safely handles temporary files like `.crdownload` or `.part` using thread-safe size stability checks).
* **Topic Classification (NLP Content Scanning):** Scans file names and document contents (supports PDF, DOCX, and TXT) for user-defined keywords (e.g., "Bank", "Gym", "University") to classify and file them into targeted directories.
* **Direct Extension Rules:** Simple rules mapping specific extensions directly to custom destinations (e.g., `.log` -> `Documents/Logs`).
* **Desktop App Window:** Run Sortix inside its own native window (`backend/desktop.py`) using `pywebview` or your browser's `--app` mode (no browser address bar) to make it feel like a native application.
* **Local LLM integration (Optional):** Supports offloading file naming and category sorting to a 100% local Ollama LLM (`llama3.2` or others) for documents that don't fit simple keyword rules.
* **Bilingual File Explorer Interface:** A clean, responsive Web UI featuring a dynamic directory tree, navigation breadcrumbs, and detailed execution logs in both English and Spanish.
* **Rich Theme System:** Toggle between fluid dark and light themes featuring hardware-accelerated circular transitions (utilizing the modern View Transitions API).
* **Cross-Platform Background Services:** Native setup scripts to easily install Sortix as a system service on Linux (systemd), macOS (LaunchAgents), or Windows (Task Scheduler).

---

## Background Service Installation (Recommended)

To keep Sortix watching your Downloads directory continuously without keeping a terminal open, install it as a background service:

### Linux (systemd user service)
```bash
cd backend/deploy
./install_linux.sh
```
*Note: The service starts automatically with your user session. Run `sudo loginctl enable-linger $USER` to keep it running when your session is closed.*

### Windows (Scheduled Task)
Open PowerShell as Administrator and run:
```powershell
cd backend\deploy
powershell -ExecutionPolicy Bypass -File install_windows.ps1
```

### macOS (LaunchAgent)
```bash
cd backend/deploy
./install_macos.sh
```

*To remove the background service at any time, run the corresponding `./uninstall_...` script from the `deploy/` folder.*

---

## Configuration & Customization

* **Custom Categories:** Base categories, folder paths, and extension maps are customized by editing [backend/config/categories.json](backend/config/categories.json).
* **Custom Topics:** Topics (e.g. "Work", "Finances") are managed directly in the Web UI under Settings -> Topics.
* **Portability:** All folder paths resolved by Sortix are relative to the user's personal home directory (`~` / `C:\Users\username`), ensuring seamless compatibility and safety across different systems.

### Advanced Settings (.env)

Customize your service by creating a `backend/.env` file:
* `SORTIX_HOST` / `SORTIX_PORT`: Customize Flask host and port.
* `SORTIX_TOKEN`: Set a shared API token (verified via `X-Sortix-Token` header), which is mandatory if you bind the host beyond `127.0.0.1` (e.g. `0.0.0.0` for a LAN dashboard).
* `SORTIX_LLM=1`: Enables the optional local LLM integration via Ollama.
* `SORTIX_LLM_URL` / `SORTIX_LLM_MODEL`: Customize LLM connection (defaults to `http://127.0.0.1:11434` and `llama3.2`).

---

## Testing

Sortix includes a self-contained integration test suite that runs against a temporary database and workspace without touching your real files:

```bash
cd backend
./.venv/bin/python tests/test_all.py
```

---

## Project Structure

```
backend/    Python server (Flask + watchdog): watcher, classifier, API
frontend/   Web UI (file-explorer style) for Topics, rules, history and translations
database/   SQLite schema (Topics, rules, move history, settings)
```

---

## Contributing

Issues and pull requests are welcome — see [CONTRIBUTING.md](CONTRIBUTING.md).
The `main` branch is protected; all changes land via reviewed PRs.

## Support the Project

If Sortix saves you time, you can support development through **GitHub Sponsors** (button at the top of the repo). Thank you!

## License

This project is licensed under the MIT License - see [LICENSE](LICENSE) for details.
© Marc Martí Torralba
