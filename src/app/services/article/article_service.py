import logging
import uuid
from datetime import datetime, timezone

from starlette.status import (
    HTTP_400_BAD_REQUEST,
    HTTP_403_FORBIDDEN,
    HTTP_404_NOT_FOUND,
)

from app.core.exceptions.api_exception import ApiErrorsCode, ApiException
from app.models import Article, Status
from app.models.security.auth_user import AuthenticatedUser
from app.storage.rds.datastore.interfaces.article import IArticle
from app.storage.rds.datastore.interfaces.category import ICategory
from app.storage.rds.datastore.interfaces.media import IMedia

LOGGER = logging.getLogger(__name__)


class ArticleService:
    def __init__(
        self,
        article_store: IArticle,
        category_store: ICategory,
        media_store: IMedia,
    ):
        self._article_store = article_store
        self._category_store = category_store
        self._media_store = media_store

    async def create_article(
        self, payload: dict, auth_user: AuthenticatedUser
    ) -> Article:
        state = payload.get("state", Status.DRAFT)

        if state not in [Status.DRAFT, Status.SUBMITTED]:
            raise ApiException(
                status_code=HTTP_400_BAD_REQUEST,
                error_code=ApiErrorsCode.INVALID_ARTICLE_STATE,
                message="An article can only be created in DRAFT or SUBMITTED state.",
            )

        article_id = str(uuid.uuid4())

        new_article = Article(
            article_id=article_id,
            title=payload["title"],
            content=payload["content"],
            tags=payload.get("tags", []),
            sources=payload.get("sources", []),
            state=state,
            user_id=auth_user.user_id,
            cover_image_id=payload.get("cover_image_id"),
            created_by=auth_user.user_id,
            created_at=datetime.now(timezone.utc),
            version=1,
            is_deleted=False,
        )

        try:
            category_ids = payload.get("category_ids", [])
            if category_ids:
                # pyrefly: ignore [missing-attribute]
                categories = await self._category_store.get_categories_by_ids(
                    category_ids
                )
                new_article.categories = categories

            media_ids = payload.get("media_ids", [])
            if media_ids:
                # pyrefly: ignore [missing-attribute]
                medias = await self._media_store.get_medias_by_ids(media_ids)
                new_article.article_medias_gallery = medias

            created_article = await self._article_store.add_article(new_article)
            LOGGER.info(
                f"Article {article_id} created successfully by {auth_user.user_id}."
            )
            return created_article

        except Exception as exc:
            LOGGER.error("Error while creating article: %s", str(exc))
            raise exc

    async def get_article(self, article_id: str) -> Article:
        try:
            article = await self._article_store.load_article(article_id)
            if article is None or article.is_deleted:
                raise ApiException(
                    status_code=HTTP_404_NOT_FOUND,
                    error_code=ApiErrorsCode.ARTICLE_NOT_FOUND,
                    message="ARTICLE_NOT_FOUND",
                )
            return article
        except Exception as exc:
            raise exc

    async def get_all_articles(
        self,
        page_size: int = 1,
        max_result: int = 20,
        direction: str = "DESC",
    ):
        LOGGER.info("Get article list")
        try:
            result = await self._article_store.load_articles(
                page_index=page_size, max_result=max_result, direction=direction
            )
            articles_count = await self._article_store.count_articles()

            return {
                "total": articles_count,
                "page_size": page_size,
                "max_result": max_result,
                "articles": [article.model_dump() for article in result],
            }
        except Exception as exc:
            LOGGER.error("Error while getting article list: %s", str(exc))
            raise exc

    async def update_and_resubmit(
        self, article_id: str, payload: dict, auth_user: AuthenticatedUser
    ) -> Article:
        article = await self.get_article(article_id)

        if article.user_id != auth_user.user_id:
            raise ApiException(
                status_code=HTTP_403_FORBIDDEN,
                error_code=ApiErrorsCode.FORBIDDEN,
                message="You are not the author of this article.",
            )

        if article.state not in [Status.DRAFT, Status.CORRECTION_REQUESTED]:
            raise ApiException(
                status_code=HTTP_400_BAD_REQUEST,
                error_code=ApiErrorsCode.INVALID_ARTICLE_TRANSITION,
                message=f"Cannot resubmit article with state {article.state}.",
            )

        article.title = payload.get("title", article.title)
        article.content = payload.get("content", article.content)
        article.tags = payload.get("tags", article.tags)
        article.sources = payload.get("sources", article.sources)
        article.cover_image_id = payload.get("cover_image_id", article.cover_image_id)
        article.state = Status.SUBMITTED
        article.updated_by = auth_user.user_id
        article.updated_at = datetime.now(timezone.utc)
        article.version += 1

        category_ids = payload.get("category_ids")
        if category_ids is not None:
            # pyrefly: ignore [missing-attribute]
            categories = await self._category_store.get_categories_by_ids(category_ids)
            article.categories = categories

        media_ids = payload.get("media_ids")
        if media_ids is not None:
            # pyrefly: ignore [missing-attribute]
            medias = await self._media_store.get_medias_by_ids(media_ids)
            article.article_medias_gallery = medias

        return await self._article_store.update_article(article)

    async def request_correction(
        self, article_id: str, admin_review: str, admin_user: AuthenticatedUser
    ) -> Article:
        article = await self.get_article(article_id)

        if article.state not in [Status.SUBMITTED, Status.PENDING]:
            raise ApiException(
                status_code=HTTP_400_BAD_REQUEST,
                error_code=ApiErrorsCode.INVALID_ARTICLE_TRANSITION,
                message=(
                    "Corrections can only be requested for "
                    "submitted or pending articles."
                ),
            )

        article.state = Status.CORRECTION_REQUESTED
        article.admin_review = admin_review
        article.updated_by = admin_user.user_id
        article.updated_at = datetime.now(timezone.utc)
        article.version += 1

        return await self._article_store.update_article(article)

    async def publish(self, article_id: str, admin_user: AuthenticatedUser) -> Article:
        article = await self.get_article(article_id)

        if article.state not in [Status.SUBMITTED, Status.APPROVED]:
            raise ApiException(
                status_code=HTTP_400_BAD_REQUEST,
                error_code=ApiErrorsCode.INVALID_ARTICLE_TRANSITION,
                message="Article is not in a publishable state.",
            )

        article.state = Status.PUBLISHED
        article.updated_by = admin_user.user_id
        article.updated_at = datetime.now(timezone.utc)
        article.version += 1

        return await self._article_store.update_article(article)

    async def delete_article(self, article_id: str, auth_user: AuthenticatedUser):
        LOGGER.info(f"Soft deleting article {article_id} by user {auth_user.user_id}")
        try:
            article = await self.get_article(article_id)

            if article.user_id != auth_user.user_id:
                raise ApiException(
                    status_code=HTTP_403_FORBIDDEN,
                    error_code=ApiErrorsCode.FORBIDDEN,
                    message="Operation not allowed.",
                )

            article.is_deleted = True
            article.updated_by = auth_user.user_id
            article.updated_at = datetime.now(timezone.utc)
            article.version += 1

            await self._article_store.update_article(article)
            LOGGER.info(f"Soft deleted article: {article_id}")

        except Exception as exc:
            LOGGER.error("Error while deleting article: %s", str(exc))
            raise exc
