import logging
from datetime import timezone
from typing import Any, Optional, Tuple

from app.api.dto.wiki.wiki_dto import ArticleResponseDTO
from app.models.wiki import Article
from app.storage.rds.clients.database_manager import DataBaseManager
from app.storage.rds.commons.sql_query_builder import (
    DeleteQueryBuilder,
    InsertQueryBuilder,
    SelectQueryBuilder,
    UpdateQueryBuilder,
)
from app.storage.rds.datastore.interfaces.article import IArticle

LOGGER = logging.getLogger(__name__)


class ArticleStore(IArticle):
    def __init__(self, database_manager: DataBaseManager):
        self._database_manager = database_manager

    async def create(self, article: Article) -> ArticleResponseDTO:
        article_iqb = InsertQueryBuilder(Article)
        article_sql, article_cols = article_iqb.sql_query()

        real_article_cols = list(Article.__table__.columns.keys())
        article_cols = [c for c in article_cols if c in real_article_cols]

        article_row = []

        for c in article_cols:
            value = getattr(article, c)

            if hasattr(value, "tzinfo") and value is not None:
                value = value.replace(tzinfo=None)

            article_row.append(value)

        async with self._database_manager.connection_pool.acquire() as connection:
            async with connection.transaction():
                await connection.execute(article_sql, *article_row)

        inserted_article = await self.get(article.article_id)

        if inserted_article is None:
            raise RuntimeError("Failed to retrieve inserted article.")

        return inserted_article

    async def get(self, article_id: str) -> Optional[ArticleResponseDTO]:
        async with self._database_manager.connection_pool.acquire() as connection:
            async with connection.transaction():
                article_sql, article_params = SelectQueryBuilder(
                    model_cls=Article,
                    where_clauses={"article_id": article_id},
                    limit=1,
                ).build_query()

                article_row = await connection.fetchrow(
                    article_sql,
                    *article_params,
                )

                if article_row is None:
                    return None

                return self.parse_article_response_kwargs(article_row=dict(article_row))

    async def get_by_title(self, title: str) -> Optional[ArticleResponseDTO]:
        async with self._database_manager.connection_pool.acquire() as connection:
            async with connection.transaction():
                article_sql, article_params = SelectQueryBuilder(
                    model_cls=Article,
                    where_clauses={"title": title},
                    limit=1,
                ).build_query()

                article_row = await connection.fetchrow(
                    article_sql,
                    *article_params,
                )

                if article_row is None:
                    return None

                return self.parse_article_response_kwargs(article_row=dict(article_row))

    async def list(
        self,
        index: int = 0,
        limit: int = 20,
    ) -> Tuple[list[ArticleResponseDTO], int]:

        index = max(0, index - 1)
        limit = max(1, limit)
        offset = index * limit

        async with self._database_manager.connection_pool.acquire() as conn:
            async with conn.transaction():

                count_sql, count_params = SelectQueryBuilder(
                    model_cls=Article,
                    selected_columns=["COUNT(1)::bigint AS total"],
                ).build_query()

                total = int(await conn.fetchval(count_sql, *count_params) or 0)

                if total == 0:
                    return [], 0

                article_sql, article_params = SelectQueryBuilder(
                    model_cls=Article,
                    order_by="created_at",
                    order_dir="DESC",
                    limit=limit,
                    offset=offset,
                ).build_query()

                rows = await conn.fetch(article_sql, *article_params)

                return (
                    [
                        self.parse_article_response_kwargs(article_row=dict(row))
                        for row in rows
                    ],
                    total,
                )

    async def update(self, article: Article) -> ArticleResponseDTO:
        updated_fields = [
            "title",
            "content",
            "slug",
            "status",
            "updated_by",
            "updated_at",
        ]

        article_sql, upd_cols, where_cols = UpdateQueryBuilder(
            model_cls=Article,
            updated_fields=updated_fields,
            where_fields=["article_id"],
            manage_version=True,
        ).sql_query()

        params = []

        for c in upd_cols:
            value = getattr(article, c)

            if hasattr(value, "tzinfo") and value is not None:
                value = value.replace(tzinfo=None)

            params.append(value)

        for c in where_cols:
            params.append(getattr(article, c))

        async with self._database_manager.connection_pool.acquire() as conn:
            async with conn.transaction():
                await conn.execute(article_sql, *params)

        updated_article = await self.get(article.article_id)

        if updated_article is None:
            raise RuntimeError("Failed to retrieve updated article.")

        return updated_article

    async def delete(self, article_id: str) -> None:
        async with self._database_manager.connection_pool.acquire() as connection:
            async with connection.transaction():

                await connection.execute(
                    """
                    DELETE FROM article_categories
                    WHERE article_id = $1
                    """,
                    article_id,
                )

                delete_sql, delete_params = DeleteQueryBuilder(
                    model_cls=Article,
                    where_clauses={"article_id": article_id},
                ).sql_query()

                await connection.execute(delete_sql, *delete_params)

    @classmethod
    def parse_article_response_kwargs(
        cls,
        *,
        article_row: dict[str, Any],
    ) -> ArticleResponseDTO:

        created_at = article_row.get("created_at")

        if created_at is not None and created_at.tzinfo is None:
            created_at = created_at.replace(tzinfo=timezone.utc)

        updated_at = article_row.get("updated_at")

        if updated_at is not None and updated_at.tzinfo is None:
            updated_at = updated_at.replace(tzinfo=timezone.utc)

        return ArticleResponseDTO(
            article_id=article_row["article_id"],
            title=article_row["title"],
            # pyrefly: ignore [bad-argument-type]
            content=article_row.get("content"),
            created_by=article_row["created_by"],
            created_at=created_at,
            updated_by=article_row.get("updated_by"),
            updated_at=updated_at,
            version=article_row["version"],
        )
