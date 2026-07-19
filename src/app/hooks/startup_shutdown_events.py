import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.configs.logger_config import init_logging
from app.storage.rds.clients.database_manager import DATA_BASE_MANAGER

LOGGER = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Démarrage de l'app")
    init_logging()

    try:
        await DATA_BASE_MANAGER.connect()
        LOGGER.info("Connexion à la base de données avec succès.")
    except Exception as e:
        LOGGER.critical(
            f"Impossible de se connecter à la base de données: {e}", exc_info=True
        )
        raise e

    yield

    print("Arrêt de l'application...")
    try:
        await DATA_BASE_MANAGER.close()
        LOGGER.info("Base de données fermée proprement.")
    except Exception as e:
        LOGGER.error(
            f"Erreur lors de la fermeture de la base de données: {e}", exc_info=True
        )
