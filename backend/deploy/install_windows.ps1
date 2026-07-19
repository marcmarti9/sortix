# Instala Sortix como una Tarea Programada de Windows: arranca en segundo
# plano al iniciar sesion (sin ventana de consola) y vigila Descargas.
#
# Ejecutar desde PowerShell (no hace falta ser administrador):
#   powershell -ExecutionPolicy Bypass -File install_windows.ps1

$ErrorActionPreference = "Stop"

$BackendDir = Split-Path -Parent $PSScriptRoot
$VenvDir = Join-Path $BackendDir ".venv"

Write-Host "==> Creando entorno virtual e instalando dependencias..."
python -m venv $VenvDir
& "$VenvDir\Scripts\pip.exe" install --quiet --upgrade pip
& "$VenvDir\Scripts\pip.exe" install --quiet -r (Join-Path $BackendDir "requirements.txt")

$PythonwPath = Join-Path $VenvDir "Scripts\pythonw.exe"

Write-Host "==> Registrando la tarea programada 'Sortix'..."
$Action = New-ScheduledTaskAction -Execute $PythonwPath -Argument '"main.py"' -WorkingDirectory $BackendDir
$Trigger = New-ScheduledTaskTrigger -AtLogOn
$Settings = New-ScheduledTaskSettingsSet -Hidden -StartWhenAvailable -RestartCount 3 -RestartInterval (New-TimeSpan -Minutes 1)

Register-ScheduledTask -TaskName "Sortix" -Action $Action -Trigger $Trigger -Settings $Settings `
    -Description "Sortix - organizador automatico de descargas" -Force | Out-Null

Start-ScheduledTask -TaskName "Sortix"

Write-Host ""
Write-Host "Sortix esta corriendo en segundo plano. Abre http://127.0.0.1:5000 para verlo."
Write-Host "Ver la tarea:   Get-ScheduledTask -TaskName Sortix"
Write-Host "Detenerla:      Stop-ScheduledTask -TaskName Sortix"
