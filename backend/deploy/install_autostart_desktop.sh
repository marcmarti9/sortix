#!/usr/bin/env bash
# Instala Martix como aplicacion de escritorio nativa con inicio automatico al encender el PC
set -euo pipefail

BACKEND_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV_DIR="$BACKEND_DIR/.venv"
APPS_DIR="$HOME/.local/share/applications"
AUTOSTART_DIR="$HOME/.config/autostart"
DESKTOP_FILE="$APPS_DIR/martix.desktop"
AUTOSTART_FILE="$AUTOSTART_DIR/martix.desktop"

# Determina si existe el ejecutable compilado en dist/Martix o usa desktop.py con el venv
DIST_BINARY="$BACKEND_DIR/dist/Martix"
if [ -f "$DIST_BINARY" ]; then
    EXEC_PATH="$DIST_BINARY"
else
    EXEC_PATH="$VENV_DIR/bin/python3 $BACKEND_DIR/desktop.py"
fi

echo "==> Configurando ejecutable de Martix en: $EXEC_PATH"
mkdir -p "$APPS_DIR" "$AUTOSTART_DIR"

sed "s#__MARTIX_EXEC__#$EXEC_PATH#g" "$BACKEND_DIR/deploy/martix.desktop" > "$DESKTOP_FILE"
cp "$DESKTOP_FILE" "$AUTOSTART_FILE"

chmod +x "$DESKTOP_FILE" "$AUTOSTART_FILE"

echo "==> Martix configurado correctamente como app de escritorio nativa:"
echo "    - Menu de aplicaciones: $DESKTOP_FILE"
echo "    - Inicio automatico al arrancar el PC: $AUTOSTART_FILE"
echo "¡Listo! Martix se abrira automaticamente en su propia ventana nativa al encender tu equipo."
