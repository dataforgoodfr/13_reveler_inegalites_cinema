#!/usr/bin/env bash
set -euo pipefail

IMAGE_NAME="${1:-reveler/source-allocine:dev}"

docker build \
	-f ingestion/scraping/allocine/Dockerfile \
	-t "${IMAGE_NAME}" \
	.

echo "Image built: ${IMAGE_NAME}"
