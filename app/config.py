import json
import os
from collections import defaultdict, deque
from functools import lru_cache

from dotenv import load_dotenv
from groq import Groq

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
PRIMARY_MODEL = os.getenv("GROQ_PRIMARY_MODEL", "groq/compound")
FALLBACK_MODEL = os.getenv("GROQ_FALLBACK_MODEL", "llama-3.3-70b-versatile")
QA_PRIMARY_MODEL = os.getenv("GROQ_QA_PRIMARY_MODEL", FALLBACK_MODEL)
MAX_INSTRUCTIONS_CHARS = int(os.getenv("MAX_INSTRUCTIONS_CHARS", "2000"))
GROQ_TIMEOUT_SECONDS = float(os.getenv("GROQ_TIMEOUT_SECONDS", "20"))
APP_ENV = os.getenv("APP_ENV", "development").lower()
APP_DEBUG_LOGS = os.getenv("APP_DEBUG_LOGS", "false").lower() == "true"
APP_SHARED_SECRET = os.getenv("APP_SHARED_SECRET", "")
APP_ID = os.getenv("APP_ID", "")
SIGNATURE_MAX_AGE_SECONDS = int(os.getenv("SIGNATURE_MAX_AGE_SECONDS", "300"))
NONCE_TTL_SECONDS = int(os.getenv("NONCE_TTL_SECONDS", "300"))
RATE_LIMIT_WINDOW_SECONDS = int(os.getenv("RATE_LIMIT_WINDOW_SECONDS", "60"))
RATE_LIMIT_MAX_REQUESTS_PER_IP = int(os.getenv("RATE_LIMIT_MAX_REQUESTS_PER_IP", "30"))
RATE_LIMIT_MAX_REQUESTS_PER_APP = int(os.getenv("RATE_LIMIT_MAX_REQUESTS_PER_APP", "120"))
ALLOWED_HOSTS = [
    host.strip() for host in os.getenv("ALLOWED_HOSTS", "*").split(",") if host.strip()
]
PRODUCTION_DOCS_ENABLED = os.getenv("PRODUCTION_DOCS_ENABLED", "false").lower() == "true"

BASE_PATH = os.path.dirname(os.path.dirname(__file__))
DATA_PATH = os.path.join(BASE_PATH, "data")
CHUNKS_PATH = os.path.join(DATA_PATH, "chunks.json")
INDEX_PATH = os.path.join(DATA_PATH, "mpnet_faiss.index")

client = Groq(api_key=GROQ_API_KEY, timeout=GROQ_TIMEOUT_SECONDS)
nonce_cache: dict[str, float] = {}
rate_limit_cache: dict[str, deque[float]] = defaultdict(deque)


@lru_cache(maxsize=1)
def get_embedding_model():
    from sentence_transformers import SentenceTransformer

    return SentenceTransformer("all-mpnet-base-v2")


@lru_cache(maxsize=1)
def get_index():
    import faiss

    return faiss.read_index(INDEX_PATH)


@lru_cache(maxsize=1)
def get_chunks():
    with open(CHUNKS_PATH, "r", encoding="utf-8") as f:
        return json.load(f)
