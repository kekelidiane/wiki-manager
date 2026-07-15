from app.storage.rds.clients.database_manager import DataBaseManager
from app.storage.rds.datastore.interfaces.health_check import IHealthCheckProvider


class HealthCheckProvider(IHealthCheckProvider):
    def __init__(self, database_manager: DataBaseManager):
        self._database_manager = database_manager

    async def health_check(self) -> bool:
        try:
            async with self._database_manager.connection_pool.acquire() as connection:
                async with connection.transaction():
                    response = await connection.fetchval("SELECT 1")
                    return response is not None and response == 1
        except Exception:
            return False
