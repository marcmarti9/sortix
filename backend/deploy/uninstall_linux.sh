#!/usr/bin/env bash
# Quita el servicio systemd de usuario de Sortix (no borra el proyecto ni la base de datos).
set -euo pipefail

UNIT_FILE="$HOME/.config/systemd/user/sortix.service"

systemctl --user disable --now sortix.service 2>/dev/null || true
rm -f "$UNIT_FILE"
systemctl --user daemon-reload

echo "Servicio de Sortix desinstalado."
