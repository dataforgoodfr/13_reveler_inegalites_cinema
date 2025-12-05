#!/bin/sh
set -euo pipefail

# Watch for the reload flag written by certbot and reload nginx when present.
(
  while :; do
    if [ -f /etc/letsencrypt/.reload ]; then
      rm -f /etc/letsencrypt/.reload
      nginx -s reload
    fi
    sleep 60
  done
) &

# Fallback periodic reload aligned with certbot renewal checks.
(
  while :; do
    sleep 12h
    nginx -s reload
  done
) &

exec nginx -g "daemon off;"
