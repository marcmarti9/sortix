#!/usr/bin/env bash
# Instala Sortix como un LaunchDaemon de macOS: arranca con el sistema
# (incluso antes de iniciar sesion), igual que el linger de systemd en Linux.
set -euo pipefail

BACKEND_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV_DIR="$BACKEND_DIR/.venv"
PLIST_LABEL="com.sortix.app"
PLIST_DEST="/Library/LaunchDaemons/${PLIST_LABEL}.plist"

echo "==> Creando entorno virtual e instalando dependencias..."
python3 -m venv "$VENV_DIR"
"$VENV_DIR/bin/pip" install --quiet --upgrade pip
"$VENV_DIR/bin/pip" install --quiet -r "$BACKEND_DIR/requirements.txt"

echo "==> Generando el LaunchDaemon (necesita tu contrasena, sudo)..."
TMP_PLIST="$(mktemp)"
sed \
    -e "s#__BACKEND_DIR__#$BACKEND_DIR#g" \
    -e "s#__PYTHON_BIN__#$VENV_DIR/bin/python3#g" \
    -e "s#__USERNAME__#$(whoami)#g" \
    "$BACKEND_DIR/deploy/com.sortix.app.plist.template" > "$TMP_PLIST"

sudo cp "$TMP_PLIST" "$PLIST_DEST"
sudo chown root:wheel "$PLIST_DEST"
sudo chmod 644 "$PLIST_DEST"
rm -f "$TMP_PLIST"

echo "==> Activando el servicio..."
sudo launchctl bootstrap system "$PLIST_DEST" 2>/dev/null || sudo launchctl load -w "$PLIST_DEST"

echo
echo "Sortix esta corriendo en segundo plano. Abre http://127.0.0.1:5000 para verlo."
echo "Estado:      sudo launchctl print system/${PLIST_LABEL}"
echo "Logs:        tail -f \"$BACKEND_DIR/sortix.log\""
echo "Detenerlo:   sudo launchctl bootout system/${PLIST_LABEL}"
