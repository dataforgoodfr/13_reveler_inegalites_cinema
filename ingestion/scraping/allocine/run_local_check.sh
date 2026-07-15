#!/usr/bin/env bash
set -euo pipefail

IMAGE_NAME="${1:-reveler/source-allocine:dev}"
CONFIG_PATH="${2:-ingestion/scraping/allocine/config.json}"

docker run --rm \
	--network host \
	-v "$(pwd)/${CONFIG_PATH}:/tmp/config.json:ro" \
	"${IMAGE_NAME}" \
	check --config /tmp/config.json
