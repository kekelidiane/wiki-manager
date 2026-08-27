import logging
from datetime import timezone
from typing import Any, List, Optional

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

    async def add_article(self, article: Article) -> Article:
        article_iqb = InsertQueryBuilder(Article)
        article_sql, article_cols = article_iqb.sql_query()

        article_row = []

        for c in article_cols:
            value = getattr(article, c)
            if hasattr(value, "tzinfo") and value is not None:
                value = value.replace(tzinfo=None)
            article_row.append(value)

        async with self._database_manager.connection_pool.acquire() as connection:
            async with connection.transaction():
                await connection.execute(article_sql, *article_row)

                if getattr(article, "categories", None):
                    for category_id in article.categories:
                        await connection.execute(
                            """
                            INSERT INTO article_categories (article_id, category_id)
                            VALUES ($1, $2) ON CONFLICT DO NOTHING
                            """,
                            article.article_id,
                            category_id,
                        )

                if getattr(article, "article_medias_gallery", None):
                    for media_id in article.article_medias_gallery:
                        await connection.execute(
                            """
                            INSERT INTO article_media_gallery (article_id, media_id)
                            VALUES ($1, $2) ON CONFLICT DO NOTHING
                            """,
                            article.article_id,
                            media_id,
                        )

        inserted_article = await self.load_article(article.article_id)

        if inserted_article is None:
            raise RuntimeError("Failed to retrieve inserted article.")

        return inserted_article

    async def load_article(self, article_id: str) -> Optional[Article]:
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

                return self._parse_article_model(article_row=dict(article_row))

    async def load_article_by_title(self, title: str) -> Optional[Article]:
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

                return self._parse_article_model(article_row=dict(article_row))

    async def load_articles(
        self, page_index: int, max_result: int, direction: str
    ) -> List[Article]:
        page_index = max(0, page_index - 1)
        limit = max(1, max_result)
        offset = page_index * limit
        order_dir = "ASC" if direction.upper() == "ASC" else "DESC"

        async with self._database_manager.connection_pool.acquire() as conn:
            async with conn.transaction():
                article_sql, article_params = SelectQueryBuilder(
                    model_cls=Article,
                    order_by="created_at",
                    order_dir=order_dir,
                    limit=limit,
                    offset=offset,
                ).build_query()

                rows = await conn.fetch(article_sql, *article_params)

                return [
                    self._parse_article_model(article_row=dict(row)) for row in rows
                ]

    async def count_articles(self) -> int:
        async with self._database_manager.connection_pool.acquire() as conn:
            async with conn.transaction():
                count_sql, count_params = SelectQueryBuilder(
                    model_cls=Article,
                    selected_columns=["COUNT(1)::bigint AS total"],
                ).build_query()

                total = await conn.fetchval(count_sql, *count_params)
                return int(total or 0)

    async def update_article(self, article: Article) -> Article:
        updated_fields = [
            "is_deleted",
            "updated_by",
            "updated_at",
        ]

        article_sql, upd_cols, where_cols = UpdateQueryBuilder(
            model_cls=Article,
            updated_fields=updated_fields,
            where_fields=["article_id"],
            manage_version=True,
        ).sql_query()

        params = [getattr(article, c) for c in upd_cols]
        for i, val in enumerate(params):
            if hasattr(val, "tzinfo") and val is not None:
                params[i] = val.replace(tzinfo=None)

        for c in where_cols:
            params.append(getattr(article, c))

        async with self._database_manager.connection_pool.acquire() as conn:
            async with conn.transaction():
                await conn.execute(article_sql, *params)

                if getattr(article, "categories", None) is not None:
                    await conn.execute(
                        "DELETE FROM article_categories WHERE article_id = $1",
                        article.article_id,
                    )
                    for category in article.categories:
                        category_id = (
                            category.category_id
                            if hasattr(category, "category_id")
                            else category
                        )
                        await conn.execute(
                            """
                            INSERT INTO article_categories (article_id, category_id)
                            VALUES ($1, $2) ON CONFLICT DO NOTHING
                            """,
                            article.article_id,
                            category_id,
                        )

                if getattr(article, "article_medias_gallery", None) is not None:
                    await conn.execute(
                        "DELETE FROM article_media_gallery WHERE article_id = $1",
                        article.article_id,
                    )
                    for media in article.article_medias_gallery:
                        media_id = (
                            media.media_id if hasattr(media, "media_id") else media
                        )
                        await conn.execute(
                            """
                            INSERT INTO article_media_gallery (article_id, media_id)
                            VALUES ($1, $2) ON CONFLICT DO NOTHING
                            """,
                            article.article_id,
                            media_id,
                        )

        return await self.load_article(article.article_id)

    async def delete_article(self, article_id: str) -> None:
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
    def _parse_article_model(cls, *, article_row: dict[str, Any]) -> Article:
        """Parse raw DB row into the Article domain model."""
        created_at = article_row.get("created_at")
        if created_at is not None and created_at.tzinfo is None:
            created_at = created_at.replace(tzinfo=timezone.utc)

        updated_at = article_row.get("updated_at")
        if updated_at is not None and updated_at.tzinfo is None:
            updated_at = updated_at.replace(tzinfo=timezone.utc)

        data = dict(article_row)
        data["created_at"] = created_at
        data["updated_at"] = updated_at

        return Article(**data)
