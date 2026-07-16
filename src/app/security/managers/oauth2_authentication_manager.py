import logging

from starlette.exceptions import HTTPException
from starlette.status import HTTP_401_UNAUTHORIZED

from app.models.security.auth_user import AuthenticatedUser
from app.security.auth_token_client import AuthTokenClient
from app.security.managers.authentication_manager import AuthenticationManager

LOGGER = logging.getLogger(__name__)


class OAuth2AuthenticationManager(AuthenticationManager):
    def __init__(self, auth_token_client: AuthTokenClient):
        self._auth_token_client = auth_token_client

    def supports(self, token: str) -> bool:
        return not self.is_jwt_token(token)

    async def authenticate(self, token: str) -> AuthenticatedUser:
        try:
            oauth_data = await self._auth_token_client.oauth2_introspect(token)

            username = oauth_data.get("username")
            if not username:
                raise HTTPException(
                    status_code=HTTP_401_UNAUTHORIZED,
                    detail="Invalid token: missing username",
                )

            return AuthenticatedUser(
                user_id=str(oauth_data.get("sub", username)),
                username=username,
                email=oauth_data.get("email", f"{username}@example.com"),
                roles=oauth_data.get("roles", []),
                scopes=oauth_data.get("scopes", []),
                groups=oauth_data.get("groups", []),
            )
        except HTTPException:
            raise
        except Exception as exc:
            LOGGER.error(f"OAuth2 Introspection failed: {exc}")
            raise HTTPException(
                status_code=HTTP_401_UNAUTHORIZED, detail="Invalid OAuth2 token"
            )
