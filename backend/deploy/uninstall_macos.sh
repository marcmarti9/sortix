#!/usr/bin/env bash
# Quita el LaunchDaemon de Sortix en macOS (no borra el proyecto ni la base de datos).
set -euo pipefail

PLIST_LABEL="com.sortix.app"
PLIST_DEST="/Library/LaunchDaemons/${PLIST_LABEL}.plist"

sudo launchctl bootout "system/${PLIST_LABEL}" 2>/dev/null || true
sudo rm -f "$PLIST_DEST"

echo "Servicio de Sortix (macOS) desinstalado."
