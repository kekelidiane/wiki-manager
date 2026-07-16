from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import HTTPException, Request
from starlette.status import HTTP_401_UNAUTHORIZED

from app.configs.environment import EnvKey
from app.models.security.auth_user import AuthenticatedUser
from app.security.auth_token_client import AuthTokenClient
from app.security.authentication_provider import AuthenticationProvider
from app.security.managers.jwt_authentication_manager import JWTAuthenticationManager


@pytest.fixture
def mock_env():
    return {
        EnvKey.WIKI_KEYCLOAK_URL: "https://keycloak.test.local",
        EnvKey.WIKI_KEYCLOAK_ISSUER: "https://keycloak.test.local/realms/wiki",
        EnvKey.WIKI_KEYCLOAK_CLIENT_ID: "wiki-api",
    }


@pytest.fixture
def mock_auth_token_client():
    client = MagicMock(spec=AuthTokenClient)
    client.get_public_key = AsyncMock(return_value="mocked_public_key")
    return client


@pytest.fixture
def jwt_manager(mock_auth_token_client, mock_env):
    return JWTAuthenticationManager(
        auth_token_client=mock_auth_token_client, env=mock_env
    )


@pytest.fixture
def auth_provider(jwt_manager):
    return AuthenticationProvider(managers=[jwt_manager])


@pytest.fixture
def valid_claims(mock_env):
    return {
        "sub": "user-123",
        "preferred_username": "john_doe",
        "email": "john.doe@test.com",
        "resource_access": {"orchestrateur": {"roles": ["employee", "manager"]}},
        "scope": "openid email",
        "iss": mock_env[EnvKey.WIKI_KEYCLOAK_ISSUER],
        "aud": mock_env[EnvKey.WIKI_KEYCLOAK_CLIENT_ID],
        "exp": 9999999999,
    }


@pytest.mark.asyncio
async def test_provider_rejects_missing_token():
    """Une requête sans token ou invalide est rejetée en 401."""
    provider = AuthenticationProvider(managers=[])
    request = MagicMock(spec=Request)
    request.headers = {}

    with pytest.raises(HTTPException) as exc_info:
        await provider(request)

    assert exc_info.value.status_code == HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
async def test_provider_rejects_non_bearer_scheme():
    """Le provider refuse un schéma d'authentification différent de 'Bearer'."""
    provider = AuthenticationProvider(managers=[])
    request = MagicMock(spec=Request)
    request.headers = {"Authorization": "Basic dXNlcjpwYXNz"}

    with pytest.raises(HTTPException) as exc_info:
        await provider(request)

    assert exc_info.value.status_code == HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
async def test_successful_jwt_authentication(auth_provider, jwt_manager, valid_claims):
    """Un token JWT valide produit un AuthenticatedUser avec les bons rôles."""

    # En mockant base64url_decode directement là où il est importé dans ton manager,
    # on court-circuite le traitement et l'erreur binascii.
    with (
        patch("jwt.decode", return_value=valid_claims),
        patch(
            "app.security.managers.jwt_authentication_manager.base64url_decode",
            return_value=b'{"kid": "key-123"}',
        ),
        patch(
            "app.security.managers.jwt_authentication_manager.orjson.loads",
            return_value={"kid": "key-123"},
        ),
        patch(
            "app.security.managers.authentication_manager.AuthenticationManager.is_jwt_token",
            return_value=True,
        ),
    ):

        request = MagicMock(spec=Request)
        request.headers = {"Authorization": "Bearer valid.mocked.jwt"}

        user = await auth_provider(request)

        assert isinstance(user, AuthenticatedUser)
        assert user.user_id == "user-123"
        assert user.username == "john_doe"
        assert user.email == "john.doe@test.com"
        assert user.has_role("employee") is True
        assert user.has_role("manager") is True
        assert user.has_role("director") is False
