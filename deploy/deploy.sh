#!/usr/bin/env bash
# Idempotent update script — run this on the VPS (not locally) every time you
# want to push a new version of the site. First-time setup steps (creating
# the venv, installing nginx/node, enabling the systemd service, certbot) are
# NOT in this script — see DEPLOY.md for that one-time setup.
set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_DIR"

echo "==> Pulling latest code"
git pull

echo "==> Installing backend dependencies"
venv/bin/pip install -r requirements.txt

echo "==> Building frontend"
cd frontend
npm ci
npm run build
cd "$REPO_DIR"

echo "==> Restarting backend service"
sudo systemctl restart ai-portfolio-backend

echo "==> Done. Check status with: sudo systemctl status ai-portfolio-backend"
