import abc
from typing import List

from app.models import Article


class IArticle(abc.ABC):
    @abc.abstractmethod
    async def add_article(self, article: Article) -> Article:
        pass

    @abc.abstractmethod
    async def update_article(self, article: Article) -> Article:
        pass

    @abc.abstractmethod
    async def load_article(self, article_id: str) -> Article | None:
        pass

    @abc.abstractmethod
    async def load_articles(
        self, page_index: int, max_result: int, direction: str
    ) -> List[Article]:
        pass

    @abc.abstractmethod
    async def count_articles(self) -> int:
        pass

    @abc.abstractmethod
    async def delete_article(self, article_id: str):
        pass
