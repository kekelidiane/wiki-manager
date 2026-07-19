from io import BytesIO
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import UploadFile

from app.configs.environment import EnvKey
from app.core.exceptions.api_exception import ApiException
from app.models.security.auth_user import AuthenticatedUser
from app.models.wiki.wiki_models import Media
from app.services.media.media_service import MediaService
from app.storage.rds.clients.blob_manager import S3Client


@pytest.fixture(scope="session")
def minio_test_env():
    """
    Génère le dictionnaire de configuration attendu par S3Client
    avec les clés EnvKey.
    """
    return {
        EnvKey.WIKI_S3_URL: "http://localhost:9000",
        EnvKey.WIKI_S3_ACCESS_KEY: "minioadmin",
        EnvKey.WIKI_S3_SECRET_KEY: "minioadmin",
        EnvKey.WIKI_S3_BUCKET_NAME: "wiki-medias",
        EnvKey.WIKI_S3_REGION: "us-east-1",
    }


@pytest.fixture
def mock_media_store():
    """Mock pour IMedia (simulation de la BDD)."""
    store = AsyncMock()
    store.add_medias = AsyncMock()
    store.load_media = AsyncMock()
    store.load_medias = AsyncMock()
    store.count_medias = AsyncMock()
    store.delete_media = AsyncMock()
    return store


@pytest.fixture
def real_blob_manager(minio_test_env):
    """Initialise un VRAI S3Client connecté au MinIO local."""
    return S3Client(environment=minio_test_env)


@pytest.fixture
def media_service(mock_media_store, real_blob_manager):
    """Initialise le service avec le mock BDD et le VRAI gestionnaire de stockage."""
    return MediaService(mock_media_store, real_blob_manager)


@pytest.fixture
def authenticated_user():
    """
    Utilisateur authentifié utilisé pour les tests upload.
    """
    return AuthenticatedUser(
        user_id="test-user-id",
    )


@pytest.mark.asyncio
async def test_upload_media_success(
    media_service,
    mock_media_store,
    minio_test_env,
    authenticated_user,
):
    """
    Vérifie qu'un fichier valide est téléversé sur le VRAI MinIO
    et enregistré en BDD.
    """

    file_content = b"fake_bytes_for_minio_test"

    mock_file = MagicMock(spec=UploadFile)
    mock_file.filename = "test_image_integration.jpg"
    mock_file.content_type = "image/jpeg"
    mock_file.read = AsyncMock(return_value=file_content)
    mock_file.file = BytesIO(file_content)

    bucket_name = minio_test_env[EnvKey.WIKI_S3_BUCKET_NAME]

    expected_url = f"http://localhost:9000/" f"{bucket_name}/test_image_integration.jpg"

    mock_media_store.add_medias.return_value = [
        Media(
            media_id="a5cfacbe-ffc8-453a-a89b-e26f10ccc218",
            url=expected_url,
            name="test_image_integration.jpg",
            content_type="image/jpeg",
            created_by="test-user-id",
        )
    ]

    # When
    result = await media_service.upload_media(
        [mock_file],
        authenticated_user,
    )

    # Then
    assert len(result) == 1
    assert "localhost:9000" in result[0].url

    mock_media_store.add_medias.assert_called_once()

    created_medias = mock_media_store.add_medias.call_args.args[0]

    assert created_medias[0].created_by == "test-user-id"


@pytest.mark.asyncio
async def test_get_media_success(media_service, mock_media_store):
    """Vérifie la récupération des métadonnées d'un média existant."""

    media_id = "1c6b4079-b789-4fa5-af9b-4982206eec50"

    mock_media = Media(
        media_id=media_id,
        url="http://localhost:9000/wiki-medias/file.png",
        name="file.png",
        content_type="image/png",
    )

    mock_media_store.load_media.return_value = mock_media

    result = await media_service.get_media(media_id)

    assert result is not None
    assert result.media_id == media_id

    mock_media_store.load_media.assert_called_once_with(media_id)


@pytest.mark.asyncio
async def test_get_media_not_found(media_service, mock_media_store):

    media_id = "unknown-uuid"

    mock_media_store.load_media.return_value = None

    with pytest.raises(ApiException) as exc_info:
        await media_service.get_media(media_id)

    assert exc_info.value.status_code == 404


@pytest.mark.asyncio
async def test_download_file_success(
    media_service,
    mock_media_store,
    real_blob_manager,
    minio_test_env,
):

    filename = "download_test.png"
    file_content = b"real_minio_bytes"

    await real_blob_manager.upload_file(
        file_content,
        filename,
        "image/png",
    )

    media_id = "1c6b4079-b789-4fa5-af9b-4982206eec50"

    bucket_name = minio_test_env[EnvKey.WIKI_S3_BUCKET_NAME]

    mock_media = Media(
        media_id=media_id,
        url=f"http://localhost:9000/{bucket_name}/{filename}",
        name=filename,
        content_type="image/png",
    )

    mock_media_store.load_media.return_value = mock_media

    content = await media_service.download_file(media_id)

    assert content == file_content

    await real_blob_manager.delete_file(filename)


@pytest.mark.asyncio
async def test_delete_media_success(
    media_service,
    mock_media_store,
    real_blob_manager,
    minio_test_env,
):

    filename = "delete_test.png"

    await real_blob_manager.upload_file(
        b"to_be_deleted",
        filename,
        "image/png",
    )

    media_id = "1c6b4079-b789-4fa5-af9b-4982206eec50"

    bucket_name = minio_test_env[EnvKey.WIKI_S3_BUCKET_NAME]

    mock_media = Media(
        media_id=media_id,
        url=f"http://localhost:9000/{bucket_name}/{filename}",
        name=filename,
        content_type="image/png",
    )

    mock_media_store.load_media.return_value = mock_media

    await media_service.delete_media(media_id)

    mock_media_store.load_media.assert_called_once_with(media_id)
    mock_media_store.delete_media.assert_called_once_with(media_id)
