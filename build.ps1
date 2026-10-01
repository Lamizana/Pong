# Construit l'exécutable Windows autonome de Pong (fichier unique).
# À exécuter sur Windows : PyInstaller ne compile pas pour Windows depuis Linux.
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

$python = if (Test-Path ".venv\Scripts\python.exe") { ".venv\Scripts\python.exe" } else { "python" }

& $python -m PyInstaller --noconfirm --clean --onefile --windowed --name Pong --add-data "pong/assets;pong/assets" main.py

Write-Host "Terminé : dist\Pong.exe"
