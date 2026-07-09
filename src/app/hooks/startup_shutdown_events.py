from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.app.configs.logger_config import init_logging


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Démarrage de l'app")
    init_logging()
    yield

    print("Arrêt de l'application...")
