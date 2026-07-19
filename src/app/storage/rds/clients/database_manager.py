import asyncio
import logging
from typing import Any, List, Optional

import asyncpg

from app.configs.environment import ENVIRONMENT_CONFIG, EnvKey
from app.storage.rds.commons.exceptions import DaoException
from app.storage.rds.datastore.interfaces.database_manager import (
    IPostgresDatabaseManager,
)

logger = logging.getLogger(__name__)


class DataBaseManager(IPostgresDatabaseManager):
    def __init__(self, configs: dict):
        self._connection_pool: Optional[asyncpg.Pool] = None
        self._config: dict = configs
        self._lock = asyncio.Lock()  # avoid initialisation conflicts

    async def _ensure_pool(self) -> asyncpg.Pool:
        if self._connection_pool is None:
            async with self._lock:
                if self._connection_pool is None:
                    logger.info(
                        "Database pool not ready. Lazy initializing connection..."
                    )
                    await self.connect()

        return self._connection_pool

    async def connect(self) -> None:
        try:
            self._connection_pool = await asyncpg.create_pool(
                self._config[EnvKey.WIKI_DB_CONNEXION],
                min_size=int(self._config[EnvKey.WIKI_DB_MIN_CON]),
                max_size=int(self._config[EnvKey.WIKI_DB_MAX_CON]),
            )
            logger.info("PostgreSQL connection pool successfully initialized.")
        except Exception as e:
            logger.error("Failed to create PostgreSQL connection pool", exc_info=True)
            raise DaoException("Unable to connect to the database.") from e

    async def close(self) -> None:
        if self._connection_pool:
            try:
                await self._connection_pool.close()
                logger.info("PostgreSQL connection pool closed.")
            except Exception as e:
                logger.error("Error while closing the connection pool", exc_info=True)
                raise DaoException(
                    "Error while disconnecting from the database."
                ) from e
            finally:
                self._connection_pool = None

    @property
    def connection_pool(self) -> asyncpg.Pool:
        if self._connection_pool is None:
            raise DaoException(
                "Database connection pool is not ready."
                "Please verify execution context."
            )
        return self._connection_pool

    async def execute(
        self, query: str, *args: Any, timeout: Optional[float] = None
    ) -> str:
        pool = await self._ensure_pool()
        try:
            return await pool.execute(query, *args, timeout=timeout)
        except Exception as exc:
            logger.error("Error executing query: %s", query, exc_info=True)
            raise DaoException(f"SQL execution error: {exc}") from exc

    async def execute_many(
        self, command: str, *args: Any, timeout: Optional[float] = None
    ) -> None:
        pool = await self._ensure_pool()
        try:
            return await pool.executemany(command, *args, timeout=timeout)
        except Exception as exc:
            logger.error("Error executing batch command: %s", command, exc_info=True)
            raise DaoException(f"SQL batch execution error: {exc}") from exc

    async def fetch(
        self, query: str, *args: Any, timeout: Optional[float] = None
    ) -> List[asyncpg.Record]:
        pool = await self._ensure_pool()
        try:
            return await pool.fetch(query, *args, timeout=timeout)
        except Exception as exc:
            logger.error("Error fetching data: %s", query, exc_info=True)
            raise DaoException(f"SQL fetch error: {exc}") from exc

    async def fetch_row(
        self, query: str, *args: Any, timeout: Optional[float] = None
    ) -> Optional[asyncpg.Record]:
        pool = await self._ensure_pool()
        try:
            return await pool.fetchrow(query, *args, timeout=timeout)
        except Exception as exc:
            logger.error("Error fetching row: %s", query, exc_info=True)
            raise DaoException(f"SQL fetch row error: {exc}") from exc

    async def fetch_value(
        self, query: str, *args: Any, column: int = 0, timeout: Optional[float] = None
    ) -> Any:
        pool = await self._ensure_pool()
        try:
            return await pool.fetchval(query, *args, column=column, timeout=timeout)
        except Exception as exc:
            logger.error("Error fetching value: %s", query, exc_info=True)
            raise DaoException(f"SQL fetch value error: {exc}") from exc


DATA_BASE_MANAGER = DataBaseManager(ENVIRONMENT_CONFIG)
