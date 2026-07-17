from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import os
from dotenv import load_dotenv
from openai import OpenAI


# Step 1: notes.txt file ko padhna

with open("notes.txt", "r") as file:
    content = file.read()

print("Poori file ka content:")
print(content)

# Step 2: Content ko chunks (lines) mein todna

chunks = content.split("\n")

print("Total chunks:", len(chunks))
print()
for i, chunk in enumerate(chunks):
    print(f"Chunk {i}: {chunk}")

# Step 3: Chunks ko clean karna

cleaned_chunks = []

for chunk in chunks:
    chunk = chunk.strip()   # shuru/aakhir ke extra spaces hatana
    if chunk != "":         # khaali lines ko skip karna
        cleaned_chunks.append(chunk)

print("Total cleaned chunks:", len(cleaned_chunks))
print()
for i, chunk in enumerate(cleaned_chunks):
    print(f"Chunk {i}: {chunk}")

# Step 4: Embedding model load karna aur chunks ko embeddings mein convert karna

print("Model load ho raha hai...")
model = SentenceTransformer('all-MiniLM-L6-v2')
print("Model load ho gaya!")
print()

# Har chunk ko embedding (numbers) mein convert karna
chunk_embeddings = model.encode(cleaned_chunks)

print("Chunk embeddings ki shape:", chunk_embeddings.shape)

# Step 5: User se sawal lena aur uska embedding banana

question = input("Apna sawal poochein: ")

question_embedding = model.encode([question])

print()
print("Sawal:", question)
print("Sawal ke embedding ki shape:", question_embedding.shape)

# Step 6: Cosine similarity nikalna — sawal ka har chunk se comparison

similarities = cosine_similarity(question_embedding, chunk_embeddings)

print("Similarity scores:")
print(similarities)

# Step 7: Sabse zyada similarity wala chunk dhoondna
best_match_index = np.argmax(similarities)

print()
print("Sabse relevant chunk ka index:", best_match_index)
print("Sabse relevant chunk:", cleaned_chunks[best_match_index])
print("Uska similarity score:", similarities[0][best_match_index])

# Step 8: OpenAI se poora jawab generate karwana



# .env file se API key load karna
load_dotenv()

# OpenAI client banana
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Retrieved chunk (context) ko sawal ke sath mila kar ek "prompt" banana
best_chunk = cleaned_chunks[best_match_index]

prompt = f"""Yahan ek information di gayi hai:

{best_chunk}

Is information ke bunyad pe, yeh sawal ka jawab dein: {question}
"""

print("prompt:", prompt)

# OpenAI ko request bhejna
response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "user", "content": prompt}
    ]
)

# Jawab print karna
answer = response.choices[0].message.content

print()
print("=== Final Answer ===")
print(answer)