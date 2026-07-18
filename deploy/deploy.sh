#!/usr/bin/env bash
# Idempotent update script — run this on the VPS every time you want to push
# a new version of the site. Requires the one-time setup in DEPLOY.md to
# already be done (repo cloned, .env created, joined to the n8n_default
# Docker network via docker-compose.yml).
set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_DIR"

echo "==> Pulling latest code"
git pull

echo "==> Rebuilding and restarting the container"
docker compose up -d --build

echo "==> Done. Check logs with: docker compose logs -f backend"
