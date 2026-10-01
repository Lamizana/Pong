#!/usr/bin/env bash
# Construit l'exécutable Linux autonome de Pong (fichier unique).
set -euo pipefail
cd "$(dirname "$0")"

# Utilise le venv du projet s'il existe, sinon le python3 courant.
PYTHON="${PYTHON:-python3}"
if [ -x ".venv/bin/python" ]; then
  PYTHON=".venv/bin/python"
fi

"$PYTHON" -m PyInstaller --noconfirm --clean --onefile --windowed \
  --name Pong main.py

echo "Terminé : dist/Pong"
