from abc import ABC, abstractmethod


class IHealthCheckProvider(ABC):
    @abstractmethod
    async def health_check(self): ...
