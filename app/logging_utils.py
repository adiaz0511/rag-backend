from app.config import APP_DEBUG_LOGS


def log_info(*parts):
    print(*parts, flush=True)


def log_debug(*parts):
    if APP_DEBUG_LOGS:
        print(*parts, flush=True)
