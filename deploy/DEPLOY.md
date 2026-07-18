# Deploying to Hostinger VPS (abdurrehmanafzal.cloud)

This guide sets up a single Ubuntu VPS serving the whole site on one domain:
Nginx serves the built React app as static files and reverse-proxies `/api/`
to a FastAPI backend running locally via systemd. One domain, one SSL cert,
no Docker.

You run all of these commands yourself over SSH — nothing here is executed
automatically.

## 0. Before you start

- **RAM**: this backend loads `sentence-transformers` (which pulls in
  `torch`) into memory at startup. Check your Hostinger VPS plan has at
  least 2GB RAM, ideally more, or the backend process may get OOM-killed.
- Confirm you can SSH into the VPS: `ssh root@<VPS_IP>` (or whatever user
  Hostinger gave you).
- This assumes Ubuntu 22.04/24.04. Adjust package manager commands if
  Hostinger provisioned a different distro.

## 1. Point the domain at the VPS

In Hostinger's DNS panel for `abdurrehmanafzal.cloud`, set:

| Type | Name | Value            |
|------|------|------------------|
| A    | @    | `<your VPS IP>`  |
| A    | www  | `<your VPS IP>`  |

DNS propagation can take a few minutes to a few hours.

## 2. Install system packages

```bash
ssh root@<VPS_IP>

apt update && apt upgrade -y
apt install -y nginx python3-venv python3-pip git curl ufw

# Node.js (needed to build the frontend on the VPS)
curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
apt install -y nodejs

# Certbot for HTTPS
apt install -y certbot python3-certbot-nginx
```

## 3. Create a deploy user (recommended over running everything as root)

```bash
adduser deploy
usermod -aG sudo deploy
su - deploy
```

Run everything below as this `deploy` user unless noted otherwise.

## 4. Clone the repo

```bash
sudo mkdir -p /var/www/rag-project
sudo chown deploy:deploy /var/www/rag-project
git clone https://github.com/AbdurRehmanAfzal/rag-project.git /var/www/rag-project
cd /var/www/rag-project
```

## 5. Backend: first-time setup

```bash
python3 -m venv venv
venv/bin/pip install --upgrade pip
venv/bin/pip install -r requirements.txt

# Create .env with your real key (never commit this file)
cat > .env <<'EOF'
OPENAI_API_KEY=sk-...your-real-key...
EOF
```

## 6. Frontend: first build

```bash
cd frontend
npm ci
npm run build   # produces frontend/dist, served directly by Nginx
cd ..
```

## 7. Enable the backend as a systemd service

```bash
sudo cp deploy/systemd/ai-portfolio-backend.service /etc/systemd/system/
sudo nano /etc/systemd/system/ai-portfolio-backend.service
# Edit WorkingDirectory / ExecStart / EnvironmentFile paths if you cloned
# somewhere other than /var/www/rag-project, and set User/Group to `deploy`.

sudo systemctl daemon-reload
sudo systemctl enable ai-portfolio-backend
sudo systemctl start ai-portfolio-backend
sudo systemctl status ai-portfolio-backend   # should show "active (running)"
```

## 8. Configure Nginx

```bash
sudo cp deploy/nginx.conf.example /etc/nginx/sites-available/abdurrehmanafzal.cloud
sudo nano /etc/nginx/sites-available/abdurrehmanafzal.cloud
# Edit the `root` path if you cloned somewhere other than /var/www/rag-project

sudo ln -s /etc/nginx/sites-available/abdurrehmanafzal.cloud /etc/nginx/sites-enabled/
sudo nginx -t   # test config syntax
sudo systemctl reload nginx
```

At this point `http://abdurrehmanafzal.cloud` should already load the site
over plain HTTP.

## 9. Enable HTTPS

```bash
sudo certbot --nginx -d abdurrehmanafzal.cloud -d www.abdurrehmanafzal.cloud
```

Certbot edits the Nginx config in place to add the HTTPS server block and an
HTTP → HTTPS redirect, and sets up auto-renewal.

## 10. Firewall

```bash
sudo ufw allow OpenSSH
sudo ufw allow 'Nginx Full'
sudo ufw enable
```

## 11. Verify

```bash
curl https://abdurrehmanafzal.cloud/api/chat \
  -X POST -H "Content-Type: application/json" \
  -d '{"query":"Tell me about your projects","history":[]}'
```

Should return JSON like `{"intent":"projects","ai_text":"..."}`. Also open
`https://abdurrehmanafzal.cloud` in a browser and click through the
suggested-prompt chips.

## Updating the site later

After the one-time setup above, every future update is just:

```bash
cd /var/www/rag-project
./deploy/deploy.sh
```

This pulls the latest commit, reinstalls Python deps, rebuilds the frontend,
and restarts the backend service. Nginx doesn't need a restart for static
file changes — it picks up the new `frontend/dist` files immediately.

## Adding the resume PDF / intro video later

- Resume: already wired up — `frontend/public/Resume-AbdurRehmanAfzal.pdf`
  is linked from the Resume pill button in `frontend/src/App.tsx`.
- Intro video: drop `intro_video.mp4` and `intro-poster.jpg` into
  `frontend/public/assets/me/`. The "Watch intro" button already appears
  automatically once these files load successfully — no code change needed.

## 12. CI/CD: auto-deploy on push (GitHub Actions)

`.github/workflows/deploy.yml` SSHes into the VPS on every push to `main`
and runs `deploy/deploy.sh` there. **This only works after you've completed
steps 1-11 above at least once manually** — the workflow updates an
existing deployment, it doesn't create one.

### 12.1 Add the deploy key to the VPS

A dedicated deploy-only SSH keypair was generated for this (not your
personal SSH key). Add its **public** key to the `deploy` user's
authorized keys on the VPS:

```bash
# on the VPS, as the deploy user
mkdir -p ~/.ssh && chmod 700 ~/.ssh
echo "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIP5FhWlnv3b1nw/RMy8FiViOCGxZAvP2E+x+XXz/5WA8 github-actions-deploy@abdurrehmanafzal.cloud" >> ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys
```

The matching **private** key was printed in the terminal when it was
generated (never committed to the repo) — you'll paste it into a GitHub
secret in the next step. If you no longer have it, generate a fresh pair
yourself (`ssh-keygen -t ed25519 -f deploy_key -N ""`) and use that instead.

### 12.2 Allow passwordless restart of the backend service

The deploy script runs `sudo systemctl restart ai-portfolio-backend`. For
that to work non-interactively over CI, grant the `deploy` user passwordless
sudo for just that command:

```bash
# on the VPS
sudo visudo -f /etc/sudoers.d/ai-portfolio-deploy
```

Add this line, then save:

```
deploy ALL=(ALL) NOPASSWD: /bin/systemctl restart ai-portfolio-backend
```

### 12.3 Add GitHub repository secrets

In your GitHub repo: **Settings → Secrets and variables → Actions → New
repository secret**. Add:

| Secret name      | Value                                              |
|------------------|-----------------------------------------------------|
| `VPS_HOST`       | Your VPS IP or hostname                             |
| `VPS_USER`       | `deploy`                                            |
| `VPS_SSH_KEY`    | The **private** key from 12.1, full contents        |
| `VPS_REPO_PATH`  | `/var/www/rag-project` (or wherever you cloned it)  |

### 12.4 Done

Push to `main` and check the **Actions** tab on GitHub — the workflow should
connect over SSH, pull, rebuild, and restart the service. Check
`sudo systemctl status ai-portfolio-backend` on the VPS afterward to confirm.
