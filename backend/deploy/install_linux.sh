#!/usr/bin/env bash
# Instala Martix como servicio de usuario systemd: arranca solo cuando
# inicias sesion y se queda vigilando Descargas en segundo plano.
set -euo pipefail

BACKEND_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV_DIR="$BACKEND_DIR/.venv"
UNIT_DIR="$HOME/.config/systemd/user"
UNIT_FILE="$UNIT_DIR/martix.service"

echo "==> Creando entorno virtual e instalando dependencias..."
python3 -m venv "$VENV_DIR"
"$VENV_DIR/bin/pip" install --quiet --upgrade pip
"$VENV_DIR/bin/pip" install --quiet -r "$BACKEND_DIR/requirements.txt"

echo "==> Generando servicio systemd de usuario..."
mkdir -p "$UNIT_DIR"
sed \
    -e "s#__BACKEND_DIR__#$BACKEND_DIR#g" \
    -e "s#__PYTHON_BIN__#$VENV_DIR/bin/python3#g" \
    "$BACKEND_DIR/deploy/martix.service.template" > "$UNIT_FILE"

echo "==> Activando el servicio..."
systemctl --user daemon-reload
systemctl --user enable --now martix.service

echo
echo "Martix esta corriendo en segundo plano. Abre http://127.0.0.1:5000 para verlo."
echo "Estado:      systemctl --user status martix.service"
echo "Logs:        journalctl --user -u martix.service -f"
echo "Detenerlo:   systemctl --user stop martix.service"
echo
echo "Nota: por defecto el servicio se para al cerrar sesion. Si quieres que"
echo "siga corriendo incluso sin sesion iniciada, ejecuta:"
echo "  sudo loginctl enable-linger \"$USER\""
