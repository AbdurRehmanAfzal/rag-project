# AI Portfolio + RAG Assistant

An interactive AI portfolio for **Abdur Rehman Afzal**, built on a Retrieval-Augmented Generation (RAG) backend. Visitors chat with an assistant that answers questions about Abdur's background using semantic search over a curated knowledge base, and the React frontend renders matching visual cards (profile, projects, experience, skills, certifications, contact) based on the intent the model detects.

A single FastAPI service both runs the RAG pipeline and serves the built frontend, so the whole thing ships as one Docker image behind Traefik.

## Features

- **RAG pipeline** – `knowledge_base.txt` is chunked and embedded once at startup with `sentence-transformers` (`all-MiniLM-L6-v2`); each query retrieves the top-k chunks by cosine similarity.
- **Intent-aware chat** – `/api/chat` uses OpenAI `gpt-4o-mini` to classify each query into an intent (`me | projects | resume | skills | contact | certifications | general`) so the frontend can render the right visual component alongside the text reply.
- **Graceful fallback** – if OpenAI is unavailable, a keyword-based responder (`get_local_response`) keeps answering on the same real data.
- **Learning Hub** – a data-driven static site at `/learn` (from `learn-hub/topics.json`, no LLM at runtime) covering AI-engineering topics.
- **Single-service deploy** – FastAPI serves the compiled React app from `frontend/dist` at `/`, so production is same-origin (no separate frontend host).

## Tech Stack

| Layer      | Technology                                                             |
| ---------- | ---------------------------------------------------------------------- |
| Backend    | Python, FastAPI, Uvicorn                                                |
| RAG / ML   | sentence-transformers, scikit-learn (cosine similarity), NumPy         |
| LLM        | OpenAI `gpt-4o-mini`                                                    |
| Frontend   | React 19, Vite, TypeScript, Tailwind CSS v4, Framer Motion             |
| Deploy     | Docker (multi-stage), Docker Compose, Traefik, GitHub Actions (CI/CD)  |

## Project Structure

```
rag-project/
├── main.py                 # FastAPI app: /ask, /api/chat, static mounts (/learn, /)
├── knowledge_base.txt      # Source content chunked + embedded for retrieval
├── requirements.txt        # Python dependencies
├── Dockerfile              # Multi-stage: build frontend, then serve from Python
├── docker-compose.yml      # Traefik-labeled service on the external n8n_default network
├── learn-hub/              # Static AI-engineering learning hub (topics.json + index.html)
├── frontend/               # React 19 + Vite + Tailwind app
│   └── src/
│       ├── App.tsx
│       ├── components/     # ExperienceTimeline, FluidCursor, Socials
│       ├── data/           # projects, experience, skills, certifications
│       └── hooks/
├── deploy/                 # DEPLOY.md + deploy.sh (VPS setup and CI script)
└── .github/workflows/      # deploy.yml (SSH deploy on push)
```

## API

### `POST /api/chat`
Used by the frontend.

```json
// Request
{ "query": "Tell me about your projects", "history": [] }

// Response
{ "intent": "projects", "ai_text": "..." }
```

### `POST /ask`
Simpler RAG endpoint that returns the answer plus its source chunks.

```json
// Request
{ "question": "Where did Abdur study?" }

// Response
{ "question": "...", "answer": "...", "sources": ["...", "..."] }
```

## Getting Started (Local)

### Prerequisites
- Python 3.11+
- Node.js 20+
- An OpenAI API key

### 1. Backend

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Create a `.env` file in the project root:

```
OPENAI_API_KEY=your-key-here
# Optional: restrict CORS in production
# ALLOWED_ORIGINS=https://your-domain
```

Run the API:

```bash
uvicorn main:app --reload --port 8000
```

The chat endpoint is now at `http://localhost:8000/api/chat`.

### 2. Frontend

```bash
cd frontend
npm install
npm run dev
```

The Vite dev server runs on `http://localhost:5173`. For a production preview, build the frontend (`npm run build`) so FastAPI serves it from `frontend/dist` at `/`.

## Docker

```bash
docker compose up -d --build
```

The multi-stage `Dockerfile` compiles the React app and serves it, `/learn`, and `/api/chat` from a single Uvicorn process on port `8000`. `docker-compose.yml` attaches to the existing external `n8n_default` network and is exposed via Traefik (see `deploy/DEPLOY.md` for the full VPS setup).

## Deployment

The service is designed to run on a shared VPS alongside Traefik (which owns ports 80/443) and other Dockerized apps. Pushing to the deploy branch triggers `.github/workflows/deploy.yml`, which SSHes to the VPS and runs `deploy/deploy.sh` (`git pull && docker compose up -d --build`). See [deploy/DEPLOY.md](deploy/DEPLOY.md) for one-time server setup.

## Security Note

`.env` currently holds real secrets and is git-ignored. Rotate any key that has ever been committed or shared, and never commit `.env`. Only `OPENAI_API_KEY` is used by `main.py`.
