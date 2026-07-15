from abc import ABC, abstractmethod


class IPostgresDatabaseManager(ABC):
    @abstractmethod
    async def connect(self):
        pass

    @abstractmethod
    async def close(self):
        pass

    @property
    @abstractmethod
    def connection_pool(self):
        pass

    @abstractmethod
    async def execute(self, query: str, *args, timeout: float | None = None):
        pass

    @abstractmethod
    async def execute_many(self, command: str, *args, timeout: float | None = None):
        pass

    @abstractmethod
    async def fetch(self, query: str, *args, timeout: float | None = None) -> list:
        pass

    @abstractmethod
    async def fetch_row(self, query: str, *args, timeout: float | None = None):
        pass

    @abstractmethod
    async def fetch_value(
        self, query: str, *args, column: int = 0, timeout: float | None = None
    ):
        pass
