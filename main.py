from fastapi import FastAPI
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import os
from dotenv import load_dotenv
from openai import OpenAI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

# .env se API key load karna
load_dotenv()

# FastAPI app banana
app = FastAPI()

# ============================================
# STARTUP: Yeh sab sirf EK BAAR, server shuru hote waqt chalega
# ============================================

print("Model load ho raha hai...")
model = SentenceTransformer('all-MiniLM-L6-v2')
print("Model load ho gaya!")

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# notes.txt padhna aur chunks banana
with open("notes.txt", "r") as file:
    content = file.read()

chunks = content.split("\n")
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

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
def read_index():
    return FileResponse("static/index.html")