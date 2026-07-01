#!/bin/bash
set -euo pipefail

echo "Bot IA Discord - Instalador"

if ! command -v python3 &> /dev/null; then
    echo "Python 3 no esta instalado"
    exit 1
fi
echo "Python 3: $(python3 --version)"

if ! command -v ffmpeg &> /dev/null; then
    echo "ADVERTENCIA: ffmpeg no esta instalado. La musica no funcionara."
    echo "Instalalo con: sudo apt install ffmpeg"
fi

VENV="venv"

if [ ! -d "$VENV" ]; then
    echo "Creando entorno virtual..."
    python3 -m venv "$VENV"
fi

echo "Instalando dependencias..."
"$VENV/bin/pip" install --upgrade pip -q
"$VENV/bin/pip" install -r requirements.txt -q

if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "Creado .env desde .env.example - editalo con tus credenciales."
fi

echo "Instalacion completa."
echo "Para ejecutar: $VENV/bin/python main.py"
