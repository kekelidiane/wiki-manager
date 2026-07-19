import logging

from fastapi.exceptions import HTTPException
from fastapi.security.http import HTTPAuthorizationCredentials, HTTPBearer
from starlette.requests import Request
from starlette.status import HTTP_401_UNAUTHORIZED

from app.configs.environment import ENVIRONMENT_CONFIG
from app.models.security.auth_user import AuthenticatedUser
from app.security.api_roles import ApiRoles
from app.security.auth_token_client import AuthTokenClient
from app.security.managers.authentication_manager import AuthenticationManager
from app.security.managers.jwt_authentication_manager import JWTAuthenticationManager
from app.security.managers.oauth2_authentication_manager import (
    OAuth2AuthenticationManager,
)

LOGGER = logging.getLogger(__name__)


class AuthenticationProvider(HTTPBearer):
    def __init__(self, authentication_managers: list[AuthenticationManager]):
        super().__init__(auto_error=True)
        self._authentication_managers = authentication_managers

    async def __call__(self, request: Request) -> AuthenticatedUser:
        credentials: HTTPAuthorizationCredentials = await super().__call__(request)
        if credentials is None:
            raise HTTPException(
                status_code=HTTP_401_UNAUTHORIZED,
                detail="no authentication code provided",
            )
        if credentials.scheme != "Bearer":
            raise HTTPException(
                status_code=HTTP_401_UNAUTHORIZED,
                detail="no valid authentication scheme provided",
            )

        token = credentials.credentials
        for authentication_manager in self._authentication_managers:
            if authentication_manager.supports(token):
                return await authentication_manager.authenticate(token)

        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED, detail="authentication error"
        )


class AuthenticationProviderMock:
    def __init__(self) -> None:
        pass

    def __call__(self) -> AuthenticatedUser:
        return AuthenticatedUser(
            user_id="9aaf7d8f-5492-41d9-97e9-cf5652ebe762",
            username="wiki_dev",
            email="developer@wiki.com",
            scopes=["read", "write"],
            roles=[ApiRoles.MANAGER, ApiRoles.EMPLOYEE, ApiRoles.DIRECTOR],
            groups=["group1", "group2"],
        )


AUTH_TOKEN_CLIENT = AuthTokenClient(ENVIRONMENT_CONFIG)

JWT_AUTHENTICATION_MANAGER = JWTAuthenticationManager(
    AUTH_TOKEN_CLIENT, ENVIRONMENT_CONFIG
)

OAUTH_AUTHENTICATION_MANAGER = OAuth2AuthenticationManager(AUTH_TOKEN_CLIENT)

AUTHENTICATION_PROVIDER = AuthenticationProviderMock()
