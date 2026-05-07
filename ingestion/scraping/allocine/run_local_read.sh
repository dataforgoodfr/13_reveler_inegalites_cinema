#!/usr/bin/env bash
set -euo pipefail

IMAGE_NAME="${1:-reveler/source-allocine:dev}"
CONFIG_PATH="${2:-ingestion/scraping/allocine/config.json}"
CATALOG_PATH="${3:-ingestion/scraping/allocine/catalog.json}"

docker run --rm \
  --network host \
  -v "$(pwd)/${CONFIG_PATH}:/tmp/config.json:ro" \
  -v "$(pwd)/${CATALOG_PATH}:/tmp/catalog.json:ro" \
  "${IMAGE_NAME}" \
  read --config /tmp/config.json --catalog /tmp/catalog.json
