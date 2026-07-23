# Quita la tarea programada de Martix (no borra el proyecto ni la base de datos).
$ErrorActionPreference = "Stop"

Stop-ScheduledTask -TaskName "Martix" -ErrorAction SilentlyContinue
Unregister-ScheduledTask -TaskName "Martix" -Confirm:$false -ErrorAction SilentlyContinue

Write-Host "Tarea programada de Martix eliminada."
