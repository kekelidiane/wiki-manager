import logging
import sys
import uuid
from contextvars import ContextVar
from logging.config import dictConfig

from starlette.middleware.base import BaseHTTPMiddleware

from src.app.configs.environment import ENVIRONMENT_CONFIG, EnvKey

APP_LOG_LEVEL = ENVIRONMENT_CONFIG[EnvKey.WIKI_LOG_LEVEL].upper()

# Store the request_id of the current request without mixing requests
_request_id: ContextVar[str | None] = ContextVar("_request_id", default=None)


def get_request_id() -> str:
    rid = _request_id.get()
    if rid is None:
        rid = str(uuid.uuid4())
        _request_id.set(rid)
    return rid


def set_request_id(rid: str | None) -> str:
    if not rid:
        rid = str(uuid.uuid4())
    _request_id.set(rid)
    return rid


# intercepts each log message and injects the request_id attribute into it
class RequestIdFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        if not hasattr(record, "request_id") or record.request_id is None:
            record.request_id = get_request_id()
        return True


# Checks if the request already contains a header; otherwise, it generates one.
class RequestIdMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        rid = request.headers.get("x-request-id") or str(uuid.uuid4())
        set_request_id(rid)
        response = await call_next(request)
        response.headers["x-request-id"] = rid
        return response


# logs configuration
LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "filters": {
        "request_id": {"()": RequestIdFilter},
    },
    "formatters": {
        "json": {
            "class": "pythonjsonlogger.jsonlogger.JsonFormatter",
            "format": (
                "[%(asctime)s.%(msecs)03d] | %(levelname)s    | "
                "%(name)s:%(funcName)s:%(lineno)d - %(message)s"
            ),
            "datefmt": "%Y-%m-%dT%H:%M:%S%z",
        },
        "defaults": {
            "class": "logging.Formatter",
            "format": "[%(asctime)s.%(msecs)03d] | %(levelname)s | "
            "%(name)s:%(funcName)s:%(lineno)d - %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
    },
    "handlers": {
        "stdout": {
            "class": "logging.StreamHandler",
            "formatter": "json",
            "filters": ["request_id"],
            "stream": sys.stdout,
        },
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "defaults",
            "stream": sys.stdout,
        },
    },
    "root": {
        "handlers": ["console"],
        "level": APP_LOG_LEVEL,
    },
    "loggers": {
        "uvicorn.access": {"level": APP_LOG_LEVEL, "propagate": True},
        "uvicorn.error": {"level": APP_LOG_LEVEL, "propagate": True},
        "alembic": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": True,
        },
        "sqlalchemy.engine": {
            "handlers": ["console"],
            "level": "WARNING",
            "propagate": True,
        },
    },
}


def init_logging() -> None:
    dictConfig(LOGGING_CONFIG)
