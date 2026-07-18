# Deploying to the Hostinger VPS (abdurrehmanafzal.cloud)

## The actual setup on this VPS

This VPS (`72.62.240.10`) is **not** a blank server — it already runs:

- **Traefik** (`n8n-traefik-1`, from `/docker/n8n/docker-compose.yml`) — the
  single reverse proxy on this box. It owns host ports 80/443 and only
  routes to containers that explicitly opt in via
  `traefik.enable=true` labels (`--providers.docker.exposedbydefault=false`).
  TLS certs come from Let's Encrypt automatically via the `mytlschallenge`
  certresolver already configured on Traefik.
- **n8n** (workflow automation), reachable only via Traefik.
- **pagereel** (`pagereel.abdurrehmanafzal.cloud`), an `nginx:alpine`
  container with no published host port — Traefik reaches it over the
  shared `n8n_default` Docker network.
- **Email (MX record)** on the bare domain — unrelated to any of the above;
  Traefik only touches HTTP/HTTPS (80/443), never mail ports, so nothing
  here can break it.

So: **no `apt install nginx`, no certbot, no systemd unit.** We add one more
Docker container next to n8n/pagereel, join the same `n8n_default` network,
and add Traefik labels so it picks up `abdurrehmanafzal.cloud` + `www`. The
repo's `Dockerfile` builds the React frontend and the FastAPI backend into
a single image; `docker-compose.yml` at the repo root defines the service
and its Traefik labels (same pattern as `/docker/pagereel/docker-compose.yml`).

## 1. DNS

Already correct — `A @` and `AAAA @` already point at this VPS
(`72.62.240.10`), and `www` is a CNAME to the bare domain. Nothing to
change here.

## 2. Clone the repo on the VPS

```bash
mkdir -p /docker/ai-portfolio
cd /docker/ai-portfolio
git clone https://github.com/AbdurRehmanAfzal/rag-project.git
cd rag-project
```

## 3. Create the backend `.env`

```bash
cat > .env <<'EOF'
OPENAI_API_KEY=sk-...your-real-key...
EOF
```

Never commit this file (it's gitignored already).

## 4. Build and start

```bash
docker compose up -d --build
```

This builds the image (Node stage compiles `frontend/`, Python stage
installs `requirements.txt` and copies the built frontend in), starts the
`ai-portfolio-backend` container, joins it to the existing `n8n_default`
network, and Traefik picks it up automatically via its labels — no Traefik
restart needed.

Check it came up clean:

```bash
docker compose logs -f backend
# Ctrl+C to stop following once you see "RAG system tayar hai!" and
# uvicorn's "Application startup complete."
```

## 5. Verify

```bash
curl -sk https://abdurrehmanafzal.cloud/api/chat \
  -X POST -H "Content-Type: application/json" \
  -d '{"query":"Tell me about your projects","history":[]}'
```

Should return JSON like `{"intent":"projects","ai_text":"..."}`. Also open
`https://abdurrehmanafzal.cloud` in a browser — first request to a new
domain may take a few seconds while Traefik obtains the Let's Encrypt cert.

Sanity check nothing else broke:

```bash
curl -sk https://pagereel.abdurrehmanafzal.cloud -o /dev/null -w "%{http_code}\n"
docker ps   # n8n, traefik, pagereel should all still show "Up"
```

## Updating the site later

```bash
cd /docker/ai-portfolio/rag-project
./deploy/deploy.sh
```

Pulls the latest commit and runs `docker compose up -d --build`, which
rebuilds the image and replaces the running container. Traefik keeps
routing to it without any config changes (labels are unchanged between
deploys).

## Adding the resume PDF / intro video later

- Resume: already wired up — `frontend/public/Resume-AbdurRehmanAfzal.pdf`
  is linked from the Resume pill button in `frontend/src/App.tsx`.
- Intro video: drop `intro_video.mp4` and `intro-poster.jpg` into
  `frontend/public/assets/me/`, then redeploy. The "Watch intro" button
  already appears automatically once these files load successfully.

## CI/CD: auto-deploy on push (GitHub Actions)

`.github/workflows/deploy.yml` SSHes into the VPS on every push to `main`
and runs `deploy/deploy.sh` there. **This only works after step 2-4 above
have been done at least once manually.**

### Add the deploy key to the VPS

A dedicated deploy-only SSH keypair was generated for this (not your
personal key). Add its **public** key to whichever user GitHub Actions will
connect as (root, unless you've created a separate deploy user):

```bash
mkdir -p ~/.ssh && chmod 700 ~/.ssh
echo "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIP5FhWlnv3b1nw/RMy8FiViOCGxZAvP2E+x+XXz/5WA8 github-actions-deploy@abdurrehmanafzal.cloud" >> ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys
```

The matching private key was shared in chat when it was generated (never
committed to the repo) — paste it into a GitHub secret below.

### Add GitHub repository secrets

**Settings → Secrets and variables → Actions → New repository secret**:

| Secret name      | Value                                                |
|------------------|-------------------------------------------------------|
| `VPS_HOST`       | `72.62.240.10`                                         |
| `VPS_USER`       | `root` (or your deploy user)                          |
| `VPS_SSH_KEY`    | The deploy private key, full contents                |
| `VPS_REPO_PATH`  | `/docker/ai-portfolio/rag-project`                    |

### Done

Push to `main` and check the **Actions** tab on GitHub — it should connect
over SSH, pull, rebuild, and restart the container. Confirm with
`docker compose logs -f backend` on the VPS afterward.
