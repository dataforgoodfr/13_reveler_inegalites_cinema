#!/bin/sh
set -euo pipefail

trap 'exit 0' TERM INT

# Renew certificates and signal nginx for immediate reload via shared volume.
while :; do
  certbot renew --quiet \
    --deploy-hook 'date +%s > /etc/letsencrypt/.reload'
  sleep 12h
done
