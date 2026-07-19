from app.storage.rds.datastore.health.health_check_provider import HealthCheckProvider
from app.storage.rds.datastore.interfaces.health_check import IHealthCheckProvider


class HealthCheckService(IHealthCheckProvider):
    def __init__(self, health_check_provider: HealthCheckProvider):
        self._health_check_provider = health_check_provider

    async def health_check(self) -> dict:
        if await self._health_check_provider.health_check():
            return {"status_code": 200, "message": "OK"}
        return {"status_code": 503, "message": "service down"}
