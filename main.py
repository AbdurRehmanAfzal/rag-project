from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import os
import json
import re
from datetime import datetime, timezone
from typing import Optional
from dotenv import load_dotenv
from openai import OpenAI
import httpx
from fastapi.staticfiles import StaticFiles

# .env se API key load karna
load_dotenv()

# FastAPI app banana
app = FastAPI()

# CORS: production is same-origin (Nginx serves the frontend and proxies
# /api/), so this is mainly a safety net for local dev / alternate hosting.
# Set ALLOWED_ORIGINS="https://your-domain" in production if needed.
allowed_origins = [o.strip() for o in os.getenv("ALLOWED_ORIGINS", "*").split(",")]
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================
# STARTUP: Yeh sab sirf EK BAAR, server shuru hote waqt chalega
# ============================================

print("Model load ho raha hai...")
model = SentenceTransformer('all-MiniLM-L6-v2')
print("Model load ho gaya!")

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

with open("knowledge_base.txt", "r", encoding="utf-8") as file:
    content = file.read()

chunks = content.split("\n\n")
cleaned_chunks = [chunk.strip() for chunk in chunks if chunk.strip() != ""]

# Chunks ke embeddings, sirf ek baar bana kar "memory mein" rakh lete hain
chunk_embeddings = model.encode(cleaned_chunks)

print("RAG system tayar hai!")

# ============================================
# REQUEST BODY: User se kya data aayega, uska "shape" define karna
# ============================================

class QuestionRequest(BaseModel):
    question: str

# ============================================
# API ENDPOINT
# ============================================

@app.post("/ask")
def ask_question(request: QuestionRequest):
    question = request.question

    # Sawal ka embedding banana
    question_embedding = model.encode([question])

    # Similarity nikalna
    similarities = cosine_similarity(question_embedding, chunk_embeddings)

    # Top 3 chunks dhoondna
    top_n = 3
    top_indices = np.argsort(similarities[0])[::-1][:top_n]
    top_chunks = [cleaned_chunks[i] for i in top_indices]

    # Prompt banana
    context = "\n".join(top_chunks)
    prompt = f"""Yahan kuch information di gayi hai:

{context}

Is information ke bunyad pe, yeh sawal ka jawab dein: {question}
"""

    # OpenAI ko bhejna
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    answer = response.choices[0].message.content

    return {
        "question": question,
        "answer": answer,
        "sources": top_chunks
    }

# ============================================
# /api/chat: portfolio chat endpoint (used by the React frontend)
# Retrieval stays the same top-k cosine-similarity search as /ask above;
# the LLM additionally classifies an `intent` so the frontend can render a
# matching visual card (profile / projects / experience / skills / contact /
# certifications) alongside the text reply.
# ============================================

class ChatMessageModel(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    query: str
    history: list[ChatMessageModel] = []

class ChatResponse(BaseModel):
    intent: str
    ai_text: str

# ============================================
# LEAD CAPTURE
# When a visitor (e.g. a recruiter) shares contact details or expresses a
# concrete hiring/collaboration intent, extract that into a structured record
# so Abdur can follow up. Runs as a background task so it never adds latency
# to or breaks the chat response. Uses OpenAI structured output (Pydantic
# schema) for reliability instead of parsing free text.
# ============================================

class LeadInfo(BaseModel):
    name: Optional[str] = Field(default=None, description="The visitor's name, if they mention it")
    email: Optional[str] = Field(default=None, description="The visitor's email address, if provided")
    phone: Optional[str] = Field(default=None, description="The visitor's phone or WhatsApp number, if provided")
    company: Optional[str] = Field(default=None, description="The company or organization the visitor represents, if mentioned")
    role_or_opportunity: Optional[str] = Field(default=None, description="The job role, project, or opportunity the visitor wants to discuss")
    message: Optional[str] = Field(default=None, description="A one-line summary of what the visitor wants")
    is_lead: bool = Field(description="True only if the visitor shared real contact details OR expressed a concrete hiring/collaboration intent; otherwise False")

# Cheap pre-filter so the extraction LLM is only called when a message
# actually looks like a lead — keeps normal Q&A traffic free of extra calls.
_EMAIL_RE = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")
_PHONE_RE = re.compile(r"(?:\+?\d[\d\s\-().]{8,}\d)")
_INTENT_PHRASES = [
    "we are hiring", "we're hiring", "were hiring", "are you available",
    "your availability", "reach out", "get in touch", "let's connect",
    "lets connect", "would love to", "i'd like to", "id like to",
    "can we schedule", "schedule a call", "book a call", "hop on a call",
    "interested in working", "work with you", "join our", "join my",
    "opportunity for you", "offer you", "contact you", "email you",
    "we have a role", "we have an opening", "open position",
]

def looks_like_lead(text: str) -> bool:
    if _EMAIL_RE.search(text) or _PHONE_RE.search(text):
        return True
    low = text.lower()
    return any(phrase in low for phrase in _INTENT_PHRASES)

def persist_lead(record: dict) -> None:
    """Best-effort local log + optional durable webhook (e.g. n8n)."""
    # Local JSONL log. Note: ephemeral inside the Docker container (lost on
    # redeploy) — the webhook below is the durable sink for production.
    try:
        with open("leads.jsonl", "a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
    except Exception as e:
        print(f"Lead file write failed: {e}")

    webhook = os.getenv("LEAD_WEBHOOK_URL")
    if webhook:
        try:
            httpx.post(webhook, json=record, timeout=10)
        except Exception as e:
            print(f"Lead webhook failed: {e}")

def capture_lead(query: str) -> None:
    """Extract and persist a lead from a single visitor message, if any.
    Designed to be scheduled via BackgroundTasks — must never raise."""
    if not os.getenv("OPENAI_API_KEY") or not looks_like_lead(query):
        return
    try:
        completion = client.beta.chat.completions.parse(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Extract lead/contact information from a message a visitor sent to Abdur Rehman Afzal's portfolio assistant. Only set is_lead to true if the visitor shared real contact details or expressed a concrete hiring or collaboration intent. Do not invent details that are not present."},
                {"role": "user", "content": query},
            ],
            response_format=LeadInfo,
        )
        lead = completion.choices[0].message.parsed
        if lead and lead.is_lead:
            record = lead.model_dump()
            record["query"] = query
            record["captured_at"] = datetime.now(timezone.utc).isoformat()
            persist_lead(record)
            print(f"🎯 Lead captured: {record}")
    except Exception as e:
        print(f"Lead extraction failed: {e}")

BASE_SYSTEM_PROMPT = """You are Abdur Rehman Afzal's AI Portfolio Assistant. Your job is to answer questions about Abdur based on the provided Knowledge Base excerpts and determine what UI component the frontend should render.

Knowledge Base (most relevant excerpts for this question):
======================
{knowledge_base}
======================

Your response MUST be valid JSON matching this schema exactly:
{{
  "intent": "me" | "projects" | "resume" | "skills" | "contact" | "certifications" | "general",
  "ai_text": "Your natural, conversational response speaking as Abdur's assistant."
}}

Rules:
- If the user asks "Tell me about yourself" or asks for a general introduction, set intent to "me".
  CRITICAL FOR "me" INTENT: The frontend will automatically display a visual profile card with his bio and skills just above your text. DO NOT repeat his basic info. Instead, provide a pleasant prompt to spark conversation.
- If the user explicitly asks to view, show, list, or see his projects or portfolio, set intent to "projects".
- If the user asks a detailed or follow-up question about a specific project (e.g. "what tech does the EID document system use?"), set intent to "general" so only the text response is rendered without showing the projects carousel again.
- If the user asks about experience, jobs, career, resume, or past work, set intent to "resume".
  CRITICAL FOR "resume" INTENT: The frontend will automatically display the visual professional experience timeline. DO NOT list every job in full. Write a warm, brief 1-2 sentence overview and ask if they have specific questions about his roles.
- If the user asks about education or where Abdur studied, set intent to "general" and answer with his education details from the Knowledge Base (BSCS, University of Central Punjab, Lahore, June 2018).
- If the user asks about certifications, certificates, or courses, set intent to "certifications".
  CRITICAL FOR "certifications" INTENT: The frontend automatically displays a visual grid of his certifications. DO NOT list every one. Write a warm, brief 1-2 sentence overview and invite them to click any card.
- If the user asks about skills or his tech stack, set intent to "skills".
- If the user wants to contact him, set intent to "contact".
  CRITICAL FOR "contact" INTENT: You MUST set `ai_text` to EXACTLY: "You can reach Abdur through the contact info above. Feel free to message him anytime. What's on your mind?"
- For anything else (follow-up questions about his journey, specific employers, specific projects, etc.), set intent to "general".
- Keep `ai_text` friendly, professional, and conversational.
- Response length: for simple greetings or when a visual card is triggered (me/projects/resume/skills/contact/certifications), keep it under 3 sentences. For detailed technical or architectural questions (e.g. "how does the multi-tenant RAG layer at ReadyChat-style systems work?", "what was the EID pipeline architecture?"), give a more detailed, structured answer (1-2 paragraphs, bullet points where helpful).
- Never invent projects, employers, dates, links, or certifications that are not in the Knowledge Base excerpts. If you don't know, say so and point to a real contact channel.
- STYLE RULE: Never use em dashes or " - " as a sentence connector in `ai_text`. Use commas, colons, or periods instead.
- Always write English contractions with proper apostrophes (e.g. "I've", "I'm", "don't", "it's"), never without the apostrophe.
"""

def get_top_chunks(query: str, top_n: int = 5) -> list[str]:
    query_embedding = model.encode([query])
    similarities = cosine_similarity(query_embedding, chunk_embeddings)
    top_indices = np.argsort(similarities[0])[::-1][:top_n]
    return [cleaned_chunks[i] for i in top_indices]

def get_local_response(query: str) -> ChatResponse:
    """Keyword fallback when the LLM is unavailable - answers stay on real data."""
    q = query.lower()

    if any(word in q for word in ["contact", "email", "linkedin", "whatsapp", "hire", "reach"]):
        return ChatResponse(intent="contact", ai_text="You can reach Abdur through the contact info above. Feel free to message him anytime. What's on your mind?")

    if any(word in q for word in ["education", "university", "study", "studied", "college", "school", "degree", "ucp"]):
        return ChatResponse(intent="general", ai_text="Abdur holds a Bachelor of Science in Computer Science from the University of Central Punjab (UCP), Lahore, Pakistan, completed in June 2018.")

    if any(word in q for word in ["certification", "certificate", "certif", "course", "udemy", "coursera", "credential"]):
        return ChatResponse(intent="certifications", ai_text="Abdur holds certifications including The AI Engineer Course 2025 (Udemy), the AI Engineer Agentic Track (Udemy), an n8n AI Agents & Automations course (Udemy), a Machine Learning Specialization (Coursera), and a Full Stack Developer Certification (EVS Training Institute). Click any card above for details.")

    if any(word in q for word in ["project", "portfolio", "chatbot", "rag", "eid", "adsgency", "palletfly", "venuegps", "workfly", "taxi", "wheat", "audit"]):
        return ChatResponse(intent="projects", ai_text="I have displayed Abdur's projects above: an AI real estate chatbot, an EID document processing system for a UAE government client, a news intelligence platform, ad-tech AI features, and several full-stack SaaS platforms.")

    if any(word in q for word in ["skill", "stack", "technology", "python", "django", "fastapi", "react", "langchain", "agent", "agentic", "automation", "voice"]):
        return ChatResponse(intent="skills", ai_text="Abdur's core strengths are Python backends (Django, FastAPI), Agentic AI and AI Automation (LangChain, CrewAI, n8n), RAG pipelines and LLM orchestration, React/Next.js/Angular frontends, plus AWS/GCP cloud infrastructure and Docker/Kubernetes deployments. He's also expanding into conversational voice agents as an emerging focus area.")

    if any(word in q for word in ["experience", "resume", "work", "job", "career", "b1 properties", "aircod", "synares", "intern"]):
        return ChatResponse(intent="resume", ai_text="I have displayed Abdur's professional timeline above, from early web development work to his current role building production AI systems at B1 Properties in Dubai, UAE.")

    if any(word in q for word in ["about", "yourself", "who are you", "abdur"]):
        return ChatResponse(intent="me", ai_text="You can see a quick summary of Abdur's background above. Ask about his AI Engineering work at B1 Properties, his RAG pipelines, or his production backend projects.")

    return ChatResponse(intent="general", ai_text="I can help you explore Abdur Rehman Afzal's profile: production AI work at B1 Properties, 7+ years of backend engineering across 9 live domains, skills, experience, education, and contact details.")

@app.post("/api/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest, background_tasks: BackgroundTasks):
    # Fire-and-forget lead capture on the visitor's message. Runs after the
    # response is sent, so it adds no latency and can't break the reply.
    background_tasks.add_task(capture_lead, request.query)

    if not client:
        return get_local_response(request.query)

    try:
        top_chunks = get_top_chunks(request.query, top_n=5)
        system_prompt = BASE_SYSTEM_PROMPT.format(knowledge_base="\n\n".join(top_chunks))

        messages = [{"role": "system", "content": system_prompt}]
        for msg in request.history:
            role = "user" if msg.role == "user" else "assistant"
            messages.append({"role": role, "content": msg.content})
        messages.append({"role": "user", "content": request.query})

        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            response_format={"type": "json_object"},
            temperature=0.3,
            max_tokens=700,
        )

        data = json.loads(completion.choices[0].message.content)
        ai_text = data.get("ai_text", "I'm not quite sure how to answer that.")

        # Restore missing apostrophes in common contractions, mirroring the style rule above
        ai_text = re.sub(r"\b[Ii]ve\b", "I've", ai_text)
        ai_text = re.sub(r"\b[Ii]m\b", "I'm", ai_text)
        ai_text = re.sub(r"\b[Dd]ont\b", "don't", ai_text)
        ai_text = re.sub(r"\b[Cc]ant\b", "can't", ai_text)
        ai_text = ai_text.replace(" — ", ", ").replace("—", ", ")

        return ChatResponse(intent=data.get("intent", "general"), ai_text=ai_text)

    except Exception as e:
        print(f"AI backend fallback used: {e}")
        return get_local_response(request.query)

# ============================================
# LEARNING HUB
# Static site generated from learn-hub/topics.json by learn-hub/build.py
# (one crawlable page per topic, sitemap, no LLM at runtime). Mounted at
# /learn before the catch-all "/" mount so it takes priority for that path.
# ============================================

class SubscribeRequest(BaseModel):
    email: str = Field(max_length=254)
    source: Optional[str] = Field(default=None, max_length=120)
    website: Optional[str] = None  # honeypot: real users never fill this

@app.post("/api/learn/subscribe")
def learn_subscribe(request: SubscribeRequest, background_tasks: BackgroundTasks):
    """Newsletter signup from the Learning Hub. Reuses the lead sink
    (leads.jsonl + optional LEAD_WEBHOOK_URL) so subscribers land in the
    same place as recruiter leads."""
    if request.website:
        # Bot filled the hidden field: pretend success, store nothing.
        return {"ok": True}
    email = request.email.strip().lower()
    if not _EMAIL_RE.fullmatch(email):
        raise HTTPException(status_code=422, detail="Please enter a valid email address.")
    record = {
        "type": "newsletter",
        "email": email,
        "source": (request.source or "learn-hub")[:120],
        "captured_at": datetime.now(timezone.utc).isoformat(),
    }
    background_tasks.add_task(persist_lead, record)
    return {"ok": True}

if os.path.isdir("learn-hub/site"):
    app.mount("/learn", StaticFiles(directory="learn-hub/site", html=True), name="learn-hub")
else:
    print("Learning Hub not built: run `python learn-hub/build.py` to generate learn-hub/site")

# Production (Docker) ships a built React app at frontend/dist.
if os.path.isdir("frontend/dist"):
    app.mount("/", StaticFiles(directory="frontend/dist", html=True), name="frontend")