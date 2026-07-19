import logging

import jwt
import orjson
from jwt.utils import base64url_decode
from starlette.exceptions import HTTPException
from starlette.status import HTTP_401_UNAUTHORIZED

from app.configs.environment import EnvKey
from app.models.security.auth_user import AuthenticatedUser
from app.security.auth_token_client import AuthTokenClient
from app.security.managers.authentication_manager import AuthenticationManager

LOGGER = logging.getLogger(__name__)


class JWTAuthenticationManager(AuthenticationManager):
    def __init__(self, auth_token_client: AuthTokenClient, env: dict):
        self._auth_token_client = auth_token_client
        self._env = env
        self._expected_audience = self._env.get(EnvKey.WIKI_KEYCLOAK_CLIENT_ID)
        self._expected_issuer = self._env.get(EnvKey.WIKI_KEYCLOAK_ISSUER)

    def supports(self, token: str) -> bool:
        return self.is_jwt_token(token)

    async def authenticate(self, token: str) -> AuthenticatedUser:
        try:
            header, _, _ = token.rsplit(".", 2)
            jwt_header = orjson.loads(base64url_decode(header))
            kid = jwt_header.get("kid")

            if not kid:
                raise HTTPException(
                    status_code=HTTP_401_UNAUTHORIZED,
                    detail="Missing 'kid' in JWT header.",
                )

            public_key = await self._auth_token_client.get_public_key(kid)
            if public_key is None:
                raise HTTPException(
                    status_code=HTTP_401_UNAUTHORIZED,
                    detail=f"No public key found for kid: {kid}",
                )

            decoded_jwt = jwt.decode(
                token,
                key=public_key,
                algorithms=["RS256", "ES256", "ES384", "ES512", "EdDSA"],
                audience=self._expected_audience,
                issuer=self._expected_issuer,
                options={
                    "verify_aud": True,
                    "verify_iss": True,
                    "verify_exp": True,
                    "require": ["exp", "iss", "sub"],
                },
            )

            resource_access = decoded_jwt.get("resource_access", {})
            orchestrateur_access = resource_access.get("orchestrateur", {})
            roles = orchestrateur_access.get("roles", [])

            scope_raw = decoded_jwt.get("scope", "")
            scopes = scope_raw.split(" ") if scope_raw else []

            return AuthenticatedUser(
                user_id=decoded_jwt["sub"],
                username=str(decoded_jwt.get("preferred_username", decoded_jwt["sub"])),
                email=decoded_jwt.get("email", ""),
                roles=roles,
                scopes=scopes,
                groups=decoded_jwt.get("groups", []),
            )

        except jwt.ExpiredSignatureError as exc:
            LOGGER.error(f"Token expired: {exc}")
            raise HTTPException(
                status_code=HTTP_401_UNAUTHORIZED, detail="JWT token is expired."
            )
        except jwt.InvalidAudienceError as exc:
            LOGGER.error(f"Invalid audience: {exc}")
            raise HTTPException(
                status_code=HTTP_401_UNAUTHORIZED, detail="Invalid token audience."
            )
        except jwt.InvalidIssuerError as exc:
            LOGGER.error(f"Invalid issuer: {exc}")
            raise HTTPException(
                status_code=HTTP_401_UNAUTHORIZED, detail="Invalid token issuer."
            )
        except (jwt.DecodeError, jwt.InvalidAlgorithmError) as exc:
            LOGGER.error(f"Token validation failed: {exc}")
            raise HTTPException(
                status_code=HTTP_401_UNAUTHORIZED,
                detail="Invalid signature or token format.",
            )
        except HTTPException:
            raise
        except Exception as exc:
            LOGGER.error(f"Unexpected authentication error: {exc}")
            raise HTTPException(
                status_code=HTTP_401_UNAUTHORIZED, detail="Authentication failed."
            )
