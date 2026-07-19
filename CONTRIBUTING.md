# Contributing to Sortix

Thanks for your interest in improving Sortix!

## Ground rules

- The `main` branch is protected: nobody (including maintainers) pushes to it
  directly. All changes go through a pull request.
- Keep Sortix **local-first and privacy-first**: no telemetry, no network
  calls to external services. The optional LLM integration must only ever
  talk to a model running on the user's own machine.
- Destination paths must always be validated as relative to the user's home
  directory (see `backend/app/security.py`).

## Development setup

```bash
cd backend
python3 -m venv .venv
./.venv/bin/pip install -r requirements.txt
./.venv/bin/python main.py        # web UI at http://127.0.0.1:5000
```

## Tests

The integration suite is self-contained (it uses a temporary HOME and a
temporary database, and never touches your real files):

```bash
cd backend
./.venv/bin/python tests/test_all.py
```

Please make sure it passes before opening a PR, and add coverage for any new
behavior.

## Reporting security issues

If you find a vulnerability, please do not open a public issue — contact the
maintainer directly instead.
