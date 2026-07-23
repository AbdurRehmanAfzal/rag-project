# 🎙️ Voice Property Concierge

A real-time voice AI you can **talk to in the browser**. It holds a natural, interruptible conversation about a real-estate search — the voice sequel to a text chatbot that lifted lead qualification 60% in production.

Built as a **cascaded pipeline** (deliberately, for engineering depth): each stage is separate and measurable, so latency and cost can be tuned and reported.

```
🎤 mic ──WebRTC──▶ VAD ──▶ Speech-to-Text ──▶ LLM ──▶ Text-to-Speech ──▶ 🔊 speaker
         (browser)  Silero    Deepgram        OpenAI     Cartesia
                                  └── barge-in: interrupt the bot mid-sentence ──┘
```

## Status: Milestone 1

- [x] **M1 — Talk to it.** Working end-to-end voice conversation, on-domain (real-estate concierge persona), with interruption handling. ← *you are here*
- [ ] M2 — RAG over real listings (reuse the main project's retrieval).
- [ ] M3 — Tool calls: `book_viewing`, `capture_lead`.
- [ ] M4 — Barge-in polish, latency/cost dashboard, eval metrics table.
- [ ] M5 — "🎙️ Talk to my AI" button embedded in the portfolio site.

## Cost

Every stage bills per minute/token, but all three services have **free tiers/credits**, so building and a light demo run at **~$0**. Guards are built in:

- **Session cap** — calls auto-end after `MAX_SESSION_SECONDS` (default 3 min).
- **Opt-in audio** — audio only streams after the visitor clicks connect (no idle billing).
- **Cheap model** — `gpt-4o-mini` by default.

| Service | Role | Free tier |
| --- | --- | --- |
| OpenAI `gpt-4o-mini` | LLM | pennies (you already have a key) |
| Deepgram | Speech-to-Text | $200 signup credit |
| Cartesia | Text-to-Speech | free tier |
| SmallWebRTC | browser transport | free, peer-to-peer, no account |

## Run it locally

Requires Python 3.10+ and a mic. From this folder:

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env            # then fill in your keys
python bot.py
```

Open **http://localhost:7860/client**, click **Connect**, allow the mic, and start talking. The bot greets you first.

> First run downloads the Silero VAD model (~20s). WebRTC needs `http://localhost` or HTTPS — browsers block mic access on plain `http://` remote hosts, which matters for VPS deploy (M5 puts it behind your existing Traefik TLS).

## How it works

[bot.py](bot.py) builds the Pipecat pipeline. The `webrtc` transport uses **SmallWebRTC** (peer-to-peer) and serves a prebuilt browser client at `/client` — no third-party media server. `enable_metrics` logs per-stage latency, which feeds the eval writeup in M4.
