import re
import time

from app.config import chunks, embedding_model, index
from app.logging_utils import log_debug, log_info


def retrieve(query, top_k=3):
    start = time.perf_counter()
    log_debug("\n--- RETRIEVE START ---")
    log_debug("Retrieve top_k:", top_k)
    log_debug("Retrieve query length:", len(query))
    log_debug("Retrieve step 1: start embedding encode")
    encode_start = time.perf_counter()
    try:
        query_embedding = embedding_model.encode([query], convert_to_numpy=True)
    except Exception as e:
        log_info("Retrieve encode error type:", type(e).__name__)
        log_info("Retrieve encode error:", str(e))
        log_info("Retrieve elapsed before encode failure:", round(time.perf_counter() - start, 3), "s")
        raise
    log_debug("Retrieve step 1 complete: embedding encode finished")
    log_debug("Embedding shape:", getattr(query_embedding, "shape", None))
    log_debug("Embedding encode elapsed:", round(time.perf_counter() - encode_start, 3), "s")

    log_debug("Retrieve step 2: start FAISS search")
    search_start = time.perf_counter()
    try:
        distances, indices = index.search(query_embedding, top_k)
    except Exception as e:
        log_info("Retrieve search error type:", type(e).__name__)
        log_info("Retrieve search error:", str(e))
        log_info("Retrieve elapsed before search failure:", round(time.perf_counter() - start, 3), "s")
        raise
    log_debug("Retrieve step 2 complete: FAISS search finished")
    log_debug("FAISS search elapsed:", round(time.perf_counter() - search_start, 3), "s")
    log_debug("Retrieve distances:", distances.tolist())
    log_debug("Retrieve indices:", indices.tolist())
    results = [chunks[i] for i in indices[0]]
    log_debug("Retrieve result count:", len(results))
    log_debug("Retrieve elapsed:", round(time.perf_counter() - start, 3), "s")
    log_debug("--- RETRIEVE END ---")
    return results


def extract_retrieval_query(query: str) -> str:
    text = (query or "").strip()

    current_question_match = re.search(
        r"Current question:\s*(.+?)(?:\n\s*\n|Recent conversation:|$)",
        text,
        re.IGNORECASE | re.DOTALL,
    )
    if current_question_match:
        extracted = current_question_match.group(1).strip()
        if extracted:
            return " ".join(extracted.split())

    lines = [line.strip() for line in text.splitlines() if line.strip()]
    if lines:
        return " ".join(lines[:2])[:300].strip()

    return text[:300].strip()
