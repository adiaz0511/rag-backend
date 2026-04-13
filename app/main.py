import time

from fastapi import Depends, FastAPI, Request
from fastapi.responses import JSONResponse
from starlette.middleware.trustedhost import TrustedHostMiddleware

from app.config import ALLOWED_HOSTS, APP_ENV, PRODUCTION_DOCS_ENABLED
from app.generation import generate_json
from app.logging_utils import log_debug, log_info
from app.prompting import build_prompt
from app.rag import extract_retrieval_query, retrieve
from app.schemas import QueryRequest, TopicRequest
from app.security import require_security_config, verify_app_request

docs_enabled = APP_ENV != "production" or PRODUCTION_DOCS_ENABLED
app = FastAPI(
    docs_url="/docs" if docs_enabled else None,
    redoc_url="/redoc" if docs_enabled else None,
    openapi_url="/openapi.json" if docs_enabled else None,
)
app.add_middleware(TrustedHostMiddleware, allowed_hosts=ALLOWED_HOSTS or ["*"])


@app.post("/ask")
async def ask(
    req: QueryRequest,
    request: Request,
    _auth: None = Depends(verify_app_request),
):
    request_start = time.perf_counter()
    log_info("\n=== /ask REQUEST START ===")
    log_info("App ID:", getattr(request.state, "app_id", "dev-bypass"))
    log_info("App Version:", getattr(request.state, "app_version", "dev-bypass"))
    log_debug("Query length:", len(req.query))

    try:
        retrieval_query = extract_retrieval_query(req.query)
        log_debug("ASK retrieval query:", retrieval_query)
        log_debug("ASK retrieval query length:", len(retrieval_query))

        log_debug("ASK step 1: retrieve context")
        context = retrieve(retrieval_query)
        log_debug("ASK retrieved chunks:", len(context))
        for idx, chunk in enumerate(context):
            log_debug(f"ASK context[{idx}] length:", len(chunk))
            log_debug(f"ASK context[{idx}] preview:", chunk[:300].replace("\n", " "))

        log_debug("ASK step 2: build prompt")
        prompt = build_prompt(req.query, context, "qa")
        log_debug("Prompt ready")
        log_debug("ASK prompt preview:")
        log_debug(prompt[:3000])

        log_debug("ASK step 3: generate JSON")
        payload = generate_json(prompt, "qa", context)
        log_info("ASK response keys:", sorted(payload.keys()))
        log_info("ASK total elapsed:", round(time.perf_counter() - request_start, 3), "s")
        log_info("=== /ask REQUEST END ===")
        return JSONResponse(payload)
    except Exception as e:
        log_info("\n=== /ask REQUEST ERROR ===")
        log_info("Error type:", type(e).__name__)
        log_info("Error:", str(e))
        log_info("ASK total elapsed before failure:", round(time.perf_counter() - request_start, 3), "s")
        raise


@app.post("/lesson")
async def lesson(
    req: TopicRequest,
    request: Request,
    _auth: None = Depends(verify_app_request),
):
    log_info("\n=== /lesson REQUEST ===")
    log_info("App ID:", getattr(request.state, "app_id", "dev-bypass"))
    log_debug("Topic length:", len(req.topic))
    log_debug("Instructions length:", len(req.instructions or ""))

    context = retrieve(req.topic)
    log_debug("Retrieved chunks:", len(context))

    prompt = build_prompt(req.topic, context, "lesson", req.instructions)
    log_debug("Prompt ready")

    return JSONResponse(generate_json(prompt, "lesson", context))


@app.post("/quiz")
async def quiz(
    req: TopicRequest,
    request: Request,
    _auth: None = Depends(verify_app_request),
):
    log_info("\n=== /quiz REQUEST ===")
    log_info("App ID:", getattr(request.state, "app_id", "dev-bypass"))
    log_debug("Topic length:", len(req.topic))

    context = retrieve(req.topic)
    log_debug("Retrieved chunks:", len(context))

    prompt = build_prompt(req.topic, context, "quiz", req.instructions)
    log_debug("Prompt ready")

    return JSONResponse(generate_json(prompt, "quiz", context))


require_security_config()
