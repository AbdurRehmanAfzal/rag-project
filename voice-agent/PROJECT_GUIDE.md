# Voice Property Concierge — Complete Project Guide

*An interview-prep walkthrough of the AI voice agent, from scratch to finished. Read this before any interview: it explains **what** was built, **how** it works, **why** each decision was made, and the **problems solved** along the way.*

---

## 1. One-line pitch

> "I built a real-time AI voice agent you can talk to in the browser. It speaks as me, and grounds every answer in my real portfolio using retrieval-augmented generation (RAG) exposed as an LLM tool call — all over a low-latency, interruptible speech pipeline."

## 2. Why I built it (the story to tell)

I'm transitioning from Senior Python Developer to AI Engineer. My production AI work (at B1 Properties, Aircod, a UAE government client) is proprietary — recruiters can't inspect it. So I built an **open, runnable, inspectable** flagship that proves depth in the areas AI teams hire for: real-time voice, RAG, agentic tool-use, and production pipeline design.

I chose **voice** because it's the rarest and most memorable of the options, and it extends my proven B1 Properties win (a text chatbot that lifted lead qualification 60%) into a harder medium.

## 3. What it does

- A visitor opens the page, clicks **Start talking**, and has a natural spoken conversation.
- The agent answers **as me (Abdur)**, in the first person, about my experience, projects, and skills.
- Every factual answer is **retrieved** from my real knowledge base — it doesn't make things up.
- You can **interrupt** it mid-sentence, like a real phone call.
- A live transcript shows both sides; an "About this project" modal explains how it was built.

## 4. High-level architecture

```
Browser (mic)                          Server (Python / FastAPI)
────────────                           ─────────────────────────
  microphone ──┐                       ┌─ Silero VAD  (detects speech / silence, enables barge-in)
               │   WebRTC audio        │
  Pipecat JS ──┼──────────────────────▶├─ Deepgram STT  (speech → text)
   SDK client  │   (/api/offer          │
               │    signaling)          ├─ OpenAI gpt-4o-mini  (LLM)
  speaker ◀────┘                       │     │
                                       │     └─▶ search_portfolio tool ─▶ knowledge.py
                                       │            (embed query, cosine top-k over KB)
                                       │
                                       └─ Cartesia TTS  (text → speech) ──▶ back to browser
```

It's a **cascaded pipeline**: each stage (VAD → STT → LLM → TTS) is a separate, swappable, measurable component. One FastAPI process (`server.py`) both serves the branded web UI and runs the Pipecat bot.

## 5. The pipeline, stage by stage

| Stage | Tool | What it does | Why this choice |
|---|---|---|---|
| Turn-taking | **Silero VAD** | Detects when the user starts/stops talking; enables interruption (barge-in) | Fast, local, the Pipecat default; no network round-trip |
| Speech-to-Text | **Deepgram** | Streams audio → text transcription | Low latency, generous free credit, strong streaming API |
| Language model | **OpenAI gpt-4o-mini** | Generates the reply; decides when to call the retrieval tool | Cheap, fast, good tool-calling; I already had a key |
| Retrieval | **sentence-transformers + NumPy** | Embeds the query, finds top-k knowledge chunks by cosine similarity | Local = ~tens of ms per query (matters for voice); $0; same model as my main RAG project |
| Text-to-Speech | **Cartesia** | Converts the reply to natural speech | Low-latency, natural voices, free tier |
| Transport | **SmallWebRTC** | Peer-to-peer audio between browser and server | No third-party media server, no account, free |
| Orchestration | **Pipecat** (Python) | Wires all stages into a streaming pipeline, handles interruptions & context | Purpose-built for real-time voice AI, Python-native |

## 6. RAG deep-dive (the part interviewers probe)

**The problem:** an LLM alone will confidently invent employers, dates, and projects. For a portfolio agent that's unacceptable.

**The solution — retrieval as a tool:**
1. At startup, `knowledge.py` reads `knowledge_base.txt`, splits it into chunks (one per paragraph), and embeds each chunk once with `all-MiniLM-L6-v2` (a sentence-transformer producing 384-dimensional vectors). Embeddings are normalized to unit length.
2. The LLM is given a tool, `search_portfolio(query)`. Its system prompt says: *always call this before answering questions about Abdur.*
3. When the user asks something, the model calls the tool. My handler embeds the query, computes **cosine similarity** against all chunk vectors (a single matrix–vector dot product, since vectors are unit length), and returns the **top-k (k=4)** most relevant chunks.
4. The model reads those chunks and speaks an answer grounded only in them.

**Why tool-calling instead of stuffing the whole file into the prompt?**
- It's *real* on-demand retrieval — the mechanism scales to a large corpus (e.g. hundreds of property listings) that would never fit in a prompt.
- It demonstrates **agentic tool-use**, which is what modern AI engineering roles want.
- It keeps each prompt focused on the relevant facts.
- (Honest trade-off: for a tiny CV-sized corpus, context-stuffing would also work and be slightly lower-latency. I chose the tool approach because it's the transferable, production-shaped pattern and it's what the B1 listings pack will need.)

**Why local embeddings, not OpenAI embeddings?** A voice agent lives or dies on latency. Local MiniLM embeds a query in tens of milliseconds with no network hop; an embeddings API call adds a round-trip on every turn. Local is faster *and* free.

## 7. Pluggable knowledge packs

`KB_SOURCE` (env var) selects what the agent knows:
- `portfolio` (default) — my `knowledge_base.txt`; the "talk to my CV" experience.
- `b1` (reserved) — a curated property-listings pack for a real-estate concierge.

Switching packs also switches the **persona** (portfolio assistant vs. property concierge). This is a clean strategy-pattern design: adding B1 later is just a new data file + registry entry, no pipeline changes.

> **Important decision:** for the B1 pack I'll use a **curated local document**, *not* a live feed from b1properties.ae. That site is my employer's production system; a public demo shouldn't depend on or republish their live/proprietary data without authorization. Curated data is safe, reliable, and tells the same story.

## 8. Cost & safety design

Voice APIs bill per minute, so cost control was built in from day one:
- **Session cap** — `MAX_SESSION_SECONDS` (default 180s) auto-ends any call.
- **Opt-in audio** — nothing streams until the visitor clicks "Start talking" (no idle billing).
- **Cheap model** — gpt-4o-mini by default.
- **Free-tier stack** — Deepgram credit, Cartesia free tier, peer-to-peer WebRTC (no media-server cost).

Net result: building and a light public demo run at **≈ $0**.

## 9. The build journey (milestones)

1. **M1 — Get one voice loop working.** Pipecat pipeline (STT→LLM→TTS) over SmallWebRTC; talk to it in the browser. The hardest 20% — end-to-end audio.
2. **Branded UI.** Replaced the generic Pipecat client with a custom, portfolio-matched page (my design system: near-black background, iris-purple accent, Space Grotesk / Inter). Added my photo, animated call button, per-turn transcript.
3. **M2 — RAG.** `knowledge.py` retrieval + the `search_portfolio` tool + a first-person "AI voice of Abdur" persona. Added suggested questions, an "About this project" modal, contact footer, and mobile responsiveness.
4. **M5 (next) — Deploy** to `talk.abdurrehmanafzal.cloud` (own Docker container + Traefik, like my other sites), with a "Talk to my AI" button on the main portfolio.

## 10. Problems I solved (great "tell me about a challenge" answers)

- **Utterances split into multiple bubbles.** Deepgram emits several "final" transcripts for one spoken sentence when you pause briefly, so "I'm… good." showed as two messages. **Fix:** accumulate all of a speaker's finals into one bubble per turn, and only start a new bubble when the other speaker takes over.
- **Duplicated bot text.** I'd wired two transcript callbacks (`onBotOutput` + the deprecated `onBotTranscript`), so each reply printed twice; and streaming chunks appended repeatedly. **Fix:** use one callback, coalesce per turn, and skip any text already shown.
- **"It still calls itself Aria."** After renaming the persona, the bot kept using the old name. Root cause: I changed the code but the running Python process still held the old prompt — a **browser refresh doesn't restart the server.** **Fix:** restart `python server.py`; also hardened the prompt with an explicit identity rule. (Lesson: know exactly what reloads on a change — static file vs. running process.)
- **Missing pieces at setup.** On a fresh machine (Python 3.14, Pipecat 1.6): the browser UI needed a separate `pipecat-ai-prebuilt` package; the quickstart imported Daily's transport which wasn't installed, so I removed it and kept the free peer-to-peer WebRTC path.
- **Secret hygiene.** A real API key almost went into `.env.example` (which is committed). **Fix:** keys live only in `.env` (git-ignored); the example holds placeholders.

## 11. What this project demonstrates (skills to claim)

Real-time voice AI · retrieval-augmented generation · agentic tool-use · LLM orchestration (Pipecat) · low-latency pipeline design · WebRTC · prompt engineering · cost & safety controls · clean pluggable architecture · full-stack delivery (Python backend + JS frontend) · production deployment (Docker + Traefik + HTTPS).

## 12. How to run it

```bash
cd voice-agent
python -m venv venv && venv\Scripts\activate       # Windows
pip install -r requirements.txt
cp .env.example .env                               # add OPENAI / DEEPGRAM / CARTESIA keys
python server.py                                   # branded UI at http://localhost:7860
# python bot.py  ->  plain Pipecat UI at /client
```

Restart `server.py` after any Python change. Static UI edits only need a browser hard-refresh.

## 13. Deployment plan (M5)

- Own subdomain **talk.abdurrehmanafzal.cloud** (not a path on the main site) — clean isolation for a memory-heavy ML service, matches my existing multi-site VPS pattern.
- Docker container + Traefik router (auto HTTPS via the existing cert resolver). HTTPS is mandatory: browsers block microphone access on non-secure origins.
- A "🎙️ Talk to my AI" button on the main portfolio links to it.

## 14. Anticipated interview questions

**Q. Why a cascaded pipeline instead of a single speech-to-speech model?**
Control and measurability. Separate stages let me swap providers, measure each stage's latency, and inject retrieval mid-pipeline. It's the more transferable, production-shaped design.

**Q. How do you keep the agent from hallucinating?**
Retrieval grounding. It must call `search_portfolio` and answer only from the returned chunks, with an explicit "never invent employers, dates, or links" rule. If the KB doesn't cover something, it says so and points to a real contact channel.

**Q. Why RAG as a tool call rather than stuffing context?**
It's real on-demand retrieval that scales beyond prompt size, and it demonstrates agentic tool-use. For a tiny corpus context-stuffing also works — I chose the pattern that generalizes.

**Q. How do you handle interruptions (barge-in)?**
Silero VAD detects the user speaking over the bot; Pipecat cancels the current bot turn so the person can take over — like a real call.

**Q. What about latency?**
Cascaded stages are all low-latency (streaming STT, a fast model, streaming TTS), retrieval is local (tens of ms), and transport is peer-to-peer WebRTC. Each stage is independently measurable, so I can profile and tune.

**Q. How do you control cost?**
Session caps, opt-in audio (no idle billing), a cheap model, and free-tier services — a public demo runs at about zero.

**Q. How would you scale this to real property data?**
Swap in a `b1` knowledge pack (curated document), keep the same retrieval tool, and add booking tools (`book_viewing`, `capture_lead`). For a large catalogue I'd move to a persistent vector store and add reranking.

**Q. What would you do next / what's missing?**
An eval harness — measure retrieval hit-rate, answer faithfulness, and per-stage latency (p50/p95). Measuring quality, not just building, is the senior differentiator.

## 15. Glossary (know these cold)

- **RAG (Retrieval-Augmented Generation):** fetch relevant facts from a knowledge source and give them to the LLM so answers are grounded, not invented.
- **Embedding:** a numeric vector representing text meaning; similar meanings → nearby vectors.
- **Cosine similarity:** measures the angle between two vectors; used to rank chunks by relevance. With unit-length vectors it's just a dot product.
- **VAD (Voice Activity Detection):** detects when someone is speaking; drives turn-taking and interruption.
- **Barge-in:** the user interrupting the bot mid-speech.
- **WebRTC:** browser real-time audio/video transport; SmallWebRTC is a serverless peer-to-peer flavour.
- **Tool / function calling:** the LLM emits a structured request to run a function (here, retrieval) and uses the result in its answer.
- **Cascaded pipeline:** separate STT → LLM → TTS stages, vs. a single speech-to-speech model.

---

*Stack: Pipecat · Deepgram · OpenAI gpt-4o-mini · Cartesia · Silero VAD · SmallWebRTC · sentence-transformers · FastAPI · vanilla JS. Built by Abdur Rehman Afzal — AI Engineer & Full-Stack Developer.*
