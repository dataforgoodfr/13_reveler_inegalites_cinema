#!/bin/sh
set -u

trap 'exit 0' TERM INT

log() { echo "[$(date -Iseconds)] certbot-loop: $*"; }

if [ ! -d /etc/letsencrypt/live ] || [ -z "$(ls -A /etc/letsencrypt/live 2>/dev/null)" ]; then
  log "WARNING: no certificate found in /etc/letsencrypt/live. 'certbot renew' will not create one — run 'certbot certonly' first to issue the initial cert."
fi

while :; do
  log "running certbot renew"
  if certbot renew --deploy-hook 'date +%s > /etc/letsencrypt/.reload'; then
    log "renew OK"
  else
    rc=$?
    log "renew FAILED (exit $rc) — retry in 12h"
  fi
  sleep 43200
done
