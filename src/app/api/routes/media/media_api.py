import io
import logging
import os

from fastapi import APIRouter, Depends, UploadFile
from fastapi.encoders import jsonable_encoder
from starlette.responses import Response, StreamingResponse
from starlette.status import HTTP_200_OK, HTTP_500_INTERNAL_SERVER_ERROR

from app.core.exceptions.api_exception import ApiException
from app.core.json.json_response import ORJSONResponse
from app.models.wiki.wiki_models import Media
from app.services.factory.services_factory import (
    WIKI_MANAGER_FACTORY,
    WikiManagerServices,
)

router = APIRouter()
LOGGER = logging.getLogger(__name__)


@router.post(path="/media/upload", name="media:upload-file")
async def upload_media(
    medias: list[UploadFile],
    media_svc: WikiManagerServices = Depends(WIKI_MANAGER_FACTORY),
):
    try:
        response: list[Media] = await media_svc.media_service.upload_media(medias)
        return ORJSONResponse(
            status_code=HTTP_200_OK, content=jsonable_encoder(response)
        )
    except ApiException as exc:
        LOGGER.error(f"Failed to upload file: Exception: {str(exc)}")
        return ORJSONResponse(status_code=exc.status_code, content=exc.message)
    except Exception as exc:
        LOGGER.error(f"Internal server error. Exception: {str(exc)}")
        return ORJSONResponse(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            content=ApiException.server_internal_error(),
        )


@router.get(path="/media/download/{media_id}", name="media:download-media")
async def download_media(
    media_id: str,
    media_svc: WikiManagerServices = Depends(WIKI_MANAGER_FACTORY),
):
    try:
        file_content = await media_svc.media_service.download_file(media_id)
        media = await media_svc.media_service.get_media(media_id)
        file_name = os.path.basename(media.url)

        return StreamingResponse(
            io.BytesIO(file_content),
            media_type="application/octet-stream",
            headers={"Content-Disposition": f"attachment; filename={file_name}"},
        )
    except ApiException as exc:
        LOGGER.error(f"Failed to download file. Exception: {str(exc)}")
        return ORJSONResponse(status_code=exc.status_code, content=exc.message)
    except Exception as exc:
        LOGGER.error(f"Internal server error. Exception: {str(exc)}")
        return ORJSONResponse(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            content=ApiException.server_internal_error(),
        )


@router.get(path="/media/get/{media_id}", name="media:get-media")
async def get_media(
    media_id: str,
    media_svc: WikiManagerServices = Depends(WIKI_MANAGER_FACTORY),
):
    try:
        response = await media_svc.media_service.get_media(media_id)
        return ORJSONResponse(
            status_code=HTTP_200_OK, content=jsonable_encoder(response)
        )
    except ApiException as exc:
        LOGGER.error(f"Failed to get file. Exception: {str(exc)}")
        return ORJSONResponse(status_code=exc.status_code, content=exc.message)
    except Exception as exc:
        LOGGER.error(f"Internal server error. Exception: {str(exc)}")
        return ORJSONResponse(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            content=ApiException.server_internal_error(),
        )


@router.get(path="/media/all", name="media:media-list")
async def get_medias(
    page_size: int | None = 1,
    max_result: int | None = 20,
    direction: str | None = "DESC",
    media_svc: WikiManagerServices = Depends(WIKI_MANAGER_FACTORY),
):
    try:
        response = await media_svc.media_service.get_all_media(
            page_size, max_result, direction
        )
        return ORJSONResponse(status_code=HTTP_200_OK, content=response)
    except ApiException as exc:
        LOGGER.error(f"Failed to get medias. Exception: {str(exc)}")
        return ORJSONResponse(status_code=exc.status_code, content=exc.message)
    except Exception as exc:
        LOGGER.error(f"Internal server error. Exception: {str(exc)}")
        return ORJSONResponse(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            content=ApiException.server_internal_error(),
        )


@router.delete(path="/media/delete/{media_id}", name="media:delete-media")
async def delete_media(
    media_id: str,
    media_svc: WikiManagerServices = Depends(WIKI_MANAGER_FACTORY),
):
    try:
        await media_svc.media_service.delete_media(media_id)
        return Response(status_code=HTTP_200_OK)
    except ApiException as exc:
        LOGGER.error(f"Failed to delete file. Exception: {str(exc)}")
        return ORJSONResponse(status_code=exc.status_code, content=exc.message)
    except Exception as exc:
        LOGGER.error(f"Internal server error. Exception: {str(exc)}")
        return ORJSONResponse(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            content=ApiException.server_internal_error(),
        )
