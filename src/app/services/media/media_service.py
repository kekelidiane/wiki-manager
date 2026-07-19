import logging
import os.path
import urllib
import uuid
from datetime import datetime, timezone

from fastapi import UploadFile
from starlette.status import HTTP_404_NOT_FOUND

from app.core.exceptions.api_exception import ApiErrorsCode, ApiException
from app.models import Media
from app.storage.rds.clients.blob_manager import S3Client
from app.storage.rds.datastore.interfaces.media import IMedia

LOGGER = logging.getLogger(__name__)


class MediaService:
    def __init__(self, media_store: IMedia, blob_provider: S3Client):
        self._media_store = media_store
        self._blob_provider = blob_provider

    async def upload_media(self, medias: list[UploadFile]) -> list[Media]:

        medias_service: list[Media] = []

        for media in medias:
            data = await media.read()
            extension = os.path.splitext(media.filename)[1]

            unique_filename = urllib.parse.quote(
                string=f"{uuid.uuid4()}{extension}", encoding="utf-8"
            )

            url = await self._blob_provider.upload_file(
                data, unique_filename, media.content_type
            )

            media_model = Media(
                **{
                    "media_id": str(uuid.uuid4()),
                    "file_name": media.filename,
                    "file_type": media.content_type,
                    "url": url,
                    "created_by": "test",
                    "created_at": datetime.now(timezone.utc),
                    "version": 1,
                }
            )
            medias_service.append(media_model)
        try:
            created_media = await self._media_store.add_medias(medias_service)
            return created_media
        except Exception as exc:
            LOGGER.error("Error while creating medias : %s", str(exc))
            raise exc

    async def download_file(self, media_id: str) -> bytes:
        try:
            media = await self._media_store.load_media(media_id)
            if media is None:
                raise ApiException(
                    status_code=HTTP_404_NOT_FOUND,
                    error_code=ApiErrorsCode.MEDIA_NOT_FOUND,
                    message="MEDIA_NOT_FOUND",
                )

            file_name = os.path.basename(media.url)
            file_content = await self._blob_provider.get_file_download_uri(file_name)
            return file_content
        except Exception as exc:
            LOGGER.error(f"Error downloading file: {exc}")
            raise exc

    async def get_media(self, media_id: str) -> Media:

        try:
            result = await self._media_store.load_media(media_id)
            if result is None:
                LOGGER.info("media not found")
                raise ApiException(
                    status_code=HTTP_404_NOT_FOUND,
                    error_code=ApiErrorsCode.MEDIA_NOT_FOUND,
                    message="MEDIA_NOT_FOUND",
                )
            LOGGER.info("media loaded: %s ", str(result))
            return result
        except Exception as exc:
            raise exc

    async def get_all_media(
        self,
        page_size: int | None = 1,
        max_result: int | None = 20,
        direction: str | None = "DESC",
    ):
        LOGGER.info("Get media list")
        try:
            result = await self._media_store.load_medias(
                page_index=page_size, max_result=max_result, direction=direction
            )
            medias_count = await self._media_store.count_medias()
            LOGGER.info(f"Get media count : {medias_count}")
            return {
                "total": medias_count,
                "page_size": page_size,
                "max_result": max_result,
                "medias": [media.model_dump() for media in result],
            }
        except Exception as exc:
            LOGGER.error("Error while getting media list: %s", str(exc))
            raise exc

    async def delete_media(self, media_id: str):
        LOGGER.info("Deleting user {}".format(media_id))
        try:
            existing_media = await self._media_store.load_media(media_id)
            if existing_media is None:
                raise ApiException(
                    status_code=HTTP_404_NOT_FOUND,
                    error_code=ApiErrorsCode.MEDIA_NOT_FOUND,
                    message="MEDIA_NOT_FOUND",
                )
            file_name = os.path.basename(existing_media.url)
            await self._media_store.delete_media(media_id)
            await self._blob_provider.delete_file(file_name)
            LOGGER.info("Deleted media : %s", str(existing_media))
        except Exception as exc:
            LOGGER.error("Error while deleting media : %s", str(exc))
            raise exc
