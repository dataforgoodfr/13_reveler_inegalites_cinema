#!/usr/bin/env bash
set -euo pipefail

IMAGE_NAME="${1:-reveler/source-allocine:dev}"

docker run --rm "${IMAGE_NAME}" spec
