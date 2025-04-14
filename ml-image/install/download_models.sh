#!/bin/bash
set -e


SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"
MODELS_DIR="$ROOT_DIR/models"

mkdir -p "$MODELS_DIR"

echo "Les modeles seront dans $MODELS_DIR"


if ! command -v gdown &> /dev/null; then
    echo "Installation de gdown..."
    pip install gdown
fi


YOLO_MODEL="models/yolov11n-face.pt"
if [ ! -f "$YOLO_MODEL" ]; then
    curl -L -o "$YOLO_MODEL" https://github.com/akanametov/yolo-face/releases/download/v0.0.0/yolov11n-face.pt
    echo "Téléchargement terminé."
else
    echo "$YOLO_MODEL déjà présent, téléchargement ignoré."
fi

FAIR_MODEL="models/res34_fair_align_multi_7_20190809.pt"
if [ ! -f "$FAIR_MODEL" ]; then
    gdown --id 113QMzQzkBDmYMs9LwzvD-jxEZdBQ5J4X -O "$FAIR_MODEL"
    echo "Téléchargement terminé."
else
    echo "$FAIR_MODEL déjà présent, téléchargement ignoré."
fi