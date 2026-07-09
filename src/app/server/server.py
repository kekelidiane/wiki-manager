import uvicorn
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware

from src.app.configs.environment import ENVIRONMENT_CONFIG, EnvKey
from src.app.configs.logger_config import LOGGING_CONFIG, RequestIdMiddleware
from src.app.configs.router_config import api_router
from src.app.hooks.startup_shutdown_events import lifespan


class WikiServer:
    def __init__(self):
        debug = ENVIRONMENT_CONFIG[EnvKey.WIKI_LOG_LEVEL].upper() == "DEBUG"
        api_name = ENVIRONMENT_CONFIG[EnvKey.WIKI_API_NAME]
        self._fastapi = FastAPI(
            debug=debug,
            title="Wiki server",
            description="Wiki service",
            version=ENVIRONMENT_CONFIG[EnvKey.WIKI_API_VERSION],
            openapi_url=api_name + "/openapi.json",
            docs_url=api_name + "/documentation",
            redoc_url=api_name + "/redoc",
            lifespan=lifespan,
        )

        self._fastapi.add_middleware(RequestIdMiddleware)

        self._fastapi.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        # Optional, this will be restricted in Task 13
        self._fastapi.add_middleware(TrustedHostMiddleware, allowed_hosts=["*"])
        self._fastapi.include_router(api_router)

    def run(self):
        uvicorn.run(
            self.fastapi,
            host=ENVIRONMENT_CONFIG[EnvKey.WIKI_BINDING_HOST],
            port=int(ENVIRONMENT_CONFIG[EnvKey.WIKI_BINDING_PORT]),
            log_level=ENVIRONMENT_CONFIG[EnvKey.WIKI_LOG_LEVEL],
            log_config=LOGGING_CONFIG,
        )

    @property
    def fastapi(self):
        return self._fastapi
