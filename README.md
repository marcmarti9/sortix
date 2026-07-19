# Sortix

Automatic downloads organizer, with a file explorer-like interface. It monitors your Downloads folder and, as soon as a new file appears, moves it to its corresponding folder:

- **Images** -> `Pictures/Downloads`
- **Videos** -> `Videos/Downloads`
- **Music** -> `Music/Downloads`
- **Compressed** -> `Downloads/Compressed`
- **Installers** (.exe, .msi, .deb, .apk...) -> `Downloads/Installers`
- **Any other document** -> `Documents/Other`
- **Everything else** -> `Downloads/Other`

Additionally, **for absolutely anything you want to group** (not just university: it could be your bank, the gym, a specific app, invoices from a supplier...), you define **Topics**: a name, a destination folder, and a set of keywords. For PDF, DOCX, and TXT files, Sortix first looks at the file name and, if there are no clear clues, scans the document's content searching for those keywords. If a document does not match any Topic, it goes to `Documents/Other` instead of forcing it into one.

Example: you create the Topic "Bank" -> `Documents/Bank`, keywords `bank, statement, iban`. The first time a PDF is downloaded from your bank, Sortix creates the `Documents/Bank` folder on its own and archives it there. The same for "Gym", "Netflix", or whatever you can think of.

You can also create simpler rules by extension (e.g. `.log` -> `Documents/Logs`), which always take priority over automatic classification.

All paths are relative to your home folder (`~` / `C:\Users\your_username`), so it works the same on Linux, Windows, and Mac.

## How to use

The idea is to set it up once (create your Topics and rules in Settings) and then let it run in the background. The main interface is a file explorer: the sidebar has Downloads, the base categories, and your Topics; clicking any of them shows its actual content, with breadcrumbs to navigate between folders. Top right: the **Active Patrol** toggle, the **Organize Now** button (for files already in Downloads), the **language** selector (ES/EN), the **light/dark theme** button (with smooth circular transitions), and the gear icon to open **Settings** (Topics and rules).

The first time you open it, if you have no Topics or rules, Settings will open automatically for you to define yours.

## Project structure

```
backend/    Python server (Flask + watchdog) that monitors and organizes
frontend/   web interface (file explorer) to manage Topics/rules
database/   SQLite schema and database (topics, rules, history, settings)
```

## Manual run (for testing)

```bash
cd backend
python3 -m venv .venv
./.venv/bin/pip install -r requirements.txt
./.venv/bin/python main.py
```

Open http://127.0.0.1:5000 in your browser.

Optional configuration in `backend/.env` (copy `backend/.env.example`):
`HOST`, `PORT`, `DOWNLOADS_DIR` (if your downloads folder is not the standard one).

## Install as a background service (recommended)

To keep Sortix watching Downloads always, without having to launch anything manually:

**Linux (systemd user service):**

```bash
cd backend/deploy
./install_linux.sh
```

Starts with your session and runs in the background. To remove it: `./uninstall_linux.sh`. To keep it active even without an active session: `sudo loginctl enable-linger $USER`.

**Windows (Scheduled Task, without window):**

```powershell
cd backend\deploy
powershell -ExecutionPolicy Bypass -File install_windows.ps1
```

To remove it: `powershell -ExecutionPolicy Bypass -File uninstall_windows.ps1`.

**macOS (LaunchDaemon, starts with the system):**

```bash
cd backend/deploy
./install_macos.sh
```

Asks for your password (sudo) because it registers to start with the system, not just on login. To remove it: `./uninstall_macos.sh`.

In all three cases, once installed, just open http://127.0.0.1:5000 when you want to toggle the patrol or adjust your Topics/rules — the background service listens there, no need to run anything else.

## Sharing with others

The project does not have any hardcoded paths or usernames: anyone who clones it and runs their system's installer (Linux/Windows/macOS) gets their own standalone installation, with their own database, their own Topics/rules, and watching their own Downloads folder. Nothing is shared between installations.

To get someone else started, they just need:

```bash
git clone <your-repo-url>
cd sortix/backend/deploy
./install_linux.sh   # or install_windows.ps1 / install_macos.sh depending on their OS
```

And from scratch, without touching anything else, it already organizes photos/videos/music/compressed/installers/documents by type. Custom Topics (bank, gym, apps...) can be added later from the interface.

## Add/remove base categories

Topics (bank, gym, apps...) are managed from the interface under Settings — no need to touch any files. Base categories (photos, videos, documents...) can only be customized by editing `backend/config/categories.json`: which extensions fall into each, and which folder they are saved to. You don't need to reset the database for this change, just restart the service (or `main.py` if running manually).
