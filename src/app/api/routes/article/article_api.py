import logging

from fastapi import APIRouter, Depends
from starlette.responses import Response
from starlette.status import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_204_NO_CONTENT,
    HTTP_500_INTERNAL_SERVER_ERROR,
)

from app.api.dto.wiki.wiki_dto import (
    CreateArticleDTO,
    RequestCorrectionDTO,
    UpdateArticleDTO,
)
from app.core.exceptions.api_exception import ApiException
from app.core.json.json_response import ORJSONResponse
from app.models.security.auth_user import AuthenticatedUser
from app.security.authentication_provider import AUTHENTICATION_PROVIDER
from app.services.factory.services_factory import (
    WIKI_MANAGER_FACTORY,
    WikiManagerServices,
)

LOGGER = logging.getLogger(__name__)

router = APIRouter()


@router.post("/create")
async def create_article(
    article_request: CreateArticleDTO,
    wiki_services: WikiManagerServices = Depends(WIKI_MANAGER_FACTORY),
    auth_user: AuthenticatedUser = Depends(AUTHENTICATION_PROVIDER),
):
    try:
        article = await wiki_services.article_service.create_article(
            article_request.model_dump(), auth_user
        )
        return ORJSONResponse(
            status_code=HTTP_201_CREATED,
            content=article.model_dump() if hasattr(article, "model_dump") else article,
        )
    except ApiException as exc:
        LOGGER.error(f"Error creating new article: {exc}")
        return ORJSONResponse(status_code=exc.status_code, content=exc.message)
    except Exception as exc:
        LOGGER.error(f"Unexpected exception: {exc}")
        return ORJSONResponse(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            content=ApiException.server_internal_error(),
        )


@router.get("/read/{article_id}")
async def read_article(
    article_id: str,
    wiki_services: WikiManagerServices = Depends(WIKI_MANAGER_FACTORY),
    auth_user: AuthenticatedUser = Depends(AUTHENTICATION_PROVIDER),
):
    try:
        article = await wiki_services.article_service.get_article(article_id)
        return ORJSONResponse(
            status_code=HTTP_200_OK,
            content=article.model_dump() if hasattr(article, "model_dump") else article,
        )
    except ApiException as exc:
        LOGGER.error(f"Error getting article: {exc}")
        return ORJSONResponse(status_code=exc.status_code, content=exc.message)
    except Exception as exc:
        LOGGER.error(f"Unexpected exception: {exc}")
        return ORJSONResponse(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            content=ApiException.server_internal_error(),
        )


@router.get("/list")
async def get_all_articles_list(
    page_size: int = 1,
    max_results: int = 20,
    direction: str = "DESC",
    wiki_services: WikiManagerServices = Depends(WIKI_MANAGER_FACTORY),
    auth_user: AuthenticatedUser = Depends(AUTHENTICATION_PROVIDER),
):
    try:
        articles_data = await wiki_services.article_service.get_all_articles(
            page_size=page_size, max_result=max_results, direction=direction
        )
        return ORJSONResponse(
            status_code=HTTP_200_OK,
            content=articles_data,
        )
    except ApiException as exc:
        LOGGER.error(f"Error getting articles list: {exc}")
        return ORJSONResponse(status_code=exc.status_code, content=exc.message)
    except Exception as exc:
        LOGGER.error(f"Unexpected exception: {exc}")
        return ORJSONResponse(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            content=ApiException.server_internal_error(),
        )


@router.put("/update-and-resubmit/{article_id}")
async def update_and_resubmit_article(
    article_id: str,
    article_request: UpdateArticleDTO,
    wiki_services: WikiManagerServices = Depends(WIKI_MANAGER_FACTORY),
    auth_user: AuthenticatedUser = Depends(AUTHENTICATION_PROVIDER),
):
    try:
        article = await wiki_services.article_service.update_and_resubmit(
            article_id, article_request.model_dump(exclude_unset=True), auth_user
        )
        return ORJSONResponse(
            status_code=HTTP_200_OK,
            content=article.model_dump() if hasattr(article, "model_dump") else article,
        )
    except ApiException as exc:
        LOGGER.error(f"Error resubmitting article: {exc}")
        return ORJSONResponse(status_code=exc.status_code, content=exc.message)
    except Exception as exc:
        LOGGER.error(f"Unexpected exception: {exc}")
        return ORJSONResponse(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            content=ApiException.server_internal_error(),
        )


@router.put("/request-correction/{article_id}")
async def request_correction_article(
    article_id: str,
    request_dto: RequestCorrectionDTO,
    wiki_services: WikiManagerServices = Depends(WIKI_MANAGER_FACTORY),
    auth_user: AuthenticatedUser = Depends(AUTHENTICATION_PROVIDER),
):
    try:
        article = await wiki_services.article_service.request_correction(
            article_id, request_dto.admin_review, auth_user
        )
        return ORJSONResponse(
            status_code=HTTP_200_OK,
            content=article.model_dump() if hasattr(article, "model_dump") else article,
        )
    except ApiException as exc:
        LOGGER.error(f"Error requesting correction: {exc}")
        return ORJSONResponse(status_code=exc.status_code, content=exc.message)
    except Exception as exc:
        LOGGER.error(f"Unexpected exception: {exc}")
        return ORJSONResponse(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            content=ApiException.server_internal_error(),
        )


@router.put("/publish/{article_id}")
async def publish_article(
    article_id: str,
    wiki_services: WikiManagerServices = Depends(WIKI_MANAGER_FACTORY),
    auth_user: AuthenticatedUser = Depends(AUTHENTICATION_PROVIDER),
):
    try:
        article = await wiki_services.article_service.publish(article_id, auth_user)
        return ORJSONResponse(
            status_code=HTTP_200_OK,
            content=article.model_dump() if hasattr(article, "model_dump") else article,
        )
    except ApiException as exc:
        LOGGER.error(f"Error publishing article: {exc}")
        return ORJSONResponse(status_code=exc.status_code, content=exc.message)
    except Exception as exc:
        LOGGER.error(f"Unexpected exception: {exc}")
        return ORJSONResponse(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            content=ApiException.server_internal_error(),
        )


@router.delete("/delete/{article_id}")
async def delete_article(
    article_id: str,
    wiki_services: WikiManagerServices = Depends(WIKI_MANAGER_FACTORY),
    auth_user: AuthenticatedUser = Depends(AUTHENTICATION_PROVIDER),
):
    try:
        await wiki_services.article_service.delete_article(article_id, auth_user)
        return Response(
            status_code=HTTP_204_NO_CONTENT,
        )
    except ApiException as exc:
        LOGGER.error(f"Error deleting article: {exc}")
        return ORJSONResponse(status_code=exc.status_code, content=exc.message)
    except Exception as exc:
        LOGGER.error(f"Unexpected exception: {exc}")
        return ORJSONResponse(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            content=ApiException.server_internal_error(),
        )
