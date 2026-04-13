import os
import json
import numpy as np
import faiss

from sentence_transformers import SentenceTransformer

# Paths
BASE_PATH = os.path.dirname(os.path.dirname(__file__))

DATA_PATH = os.path.join(BASE_PATH, "data")

CHUNKS_PATH = os.path.join(DATA_PATH, "chunks.json")
INDEX_PATH = os.path.join(DATA_PATH, "mpnet_faiss.index")

# Load embedding model (must match notebook)
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
print(f"Chunks: {len(chunks)}")
print(f"Index size: {index.ntotal}")


# Retrieval function
def retrieve(query, top_k=5):
    query_embedding = embedding_model.encode([query], convert_to_numpy=True)
    distances, indices = index.search(query_embedding, top_k)
    return [chunks[i] for i in indices[0]]


# Test query
query = "What temperature is considered dangerous after transplant?"

print("\nQuery:", query)

results = retrieve(query)

for i, r in enumerate(results):
    print("\n" + "=" * 60)
    print(f"Result {i+1}")
    print(r[:400])