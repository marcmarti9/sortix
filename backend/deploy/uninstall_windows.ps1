# Quita la tarea programada de Sortix (no borra el proyecto ni la base de datos).
$ErrorActionPreference = "Stop"

Stop-ScheduledTask -TaskName "Sortix" -ErrorAction SilentlyContinue
Unregister-ScheduledTask -TaskName "Sortix" -Confirm:$false -ErrorAction SilentlyContinue

Write-Host "Tarea programada de Sortix eliminada."
