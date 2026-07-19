from abc import ABC, abstractmethod


class IMedia(ABC):
    @abstractmethod
    async def add_medias(self, *args, **kwargs):
        raise NotImplementedError

    @abstractmethod
    async def load_medias(self, *args, **kwargs):
        raise NotImplementedError

    @abstractmethod
    async def load_media(self, *args, **kwargs):
        raise NotImplementedError

    @abstractmethod
    async def delete_media(self, *args, **kwargs):
        raise NotImplementedError

    async def count_medias(self):
        raise NotImplementedError
