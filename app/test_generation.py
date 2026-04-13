import os
import json
import faiss

from sentence_transformers import SentenceTransformer
from groq import Groq
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Paths
BASE_PATH = os.path.dirname(os.path.dirname(__file__))
DATA_PATH = os.path.join(BASE_PATH, "data")

CHUNKS_PATH = os.path.join(DATA_PATH, "chunks.json")
INDEX_PATH = os.path.join(DATA_PATH, "mpnet_faiss.index")

# Load embedding model
print("Loading embedding model...")
embedding_model = SentenceTransformer("all-mpnet-base-v2")

# Load FAISS index
print("Loading FAISS index...")
index = faiss.read_index(INDEX_PATH)

# Load chunks
print("Loading chunks...")
with open(CHUNKS_PATH, "r", encoding="utf-8") as f:
    chunks = json.load(f)

print("System loaded")


# Initialize Groq client
client = Groq(api_key=GROQ_API_KEY)


# Retrieval
def retrieve(query, top_k=5):
    query_embedding = embedding_model.encode([query], convert_to_numpy=True)
    distances, indices = index.search(query_embedding, top_k)
    return [chunks[i] for i in indices[0]]


# Prompt builder
def build_prompt(query, context_chunks):
    context = "\n\n".join(context_chunks)

    prompt = f"""
You are a medical assistant helping parents understand a transplant care manual.

Use only the information in the context below.

Context:
{context}

Question:
{query}

Answer:
"""
    return prompt.strip()


# Generation
def generate(prompt):
    response = client.chat.completions.create(
        model="groq/compound",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2
    )

    return response.choices[0].message.content


# Test query
query = "What temperature is considered dangerous after transplant?"

print("\nQuery:", query)

context_chunks = retrieve(query)

print("\nRetrieved Chunks:")
for i, c in enumerate(context_chunks):
    print("\n" + "=" * 60)
    print(f"Chunk {i+1}")
    print(c[:300])

prompt = build_prompt(query, context_chunks)

print("\nGenerating answer...\n")

answer = generate(prompt)

print("Answer:\n")
print(answer)