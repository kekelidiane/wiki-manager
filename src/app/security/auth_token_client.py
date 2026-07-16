import asyncio
import logging

import httpx
import orjson
from jwt.algorithms import get_default_algorithms
from starlette.exceptions import HTTPException
from starlette.status import HTTP_401_UNAUTHORIZED

from app.configs.environment import EnvKey

LOGGER = logging.getLogger(__name__)


class AuthTokenClient:
    def __init__(self, env: dict):
        self._env = env
        self._jwks_cache = {}
        self._client = httpx.AsyncClient(timeout=3.0)

    async def get_public_key(self, kid: str):
        if kid in self._jwks_cache:
            return self._jwks_cache[kid]

        try:
            await self._refresh_jwks()
        except Exception as exc:
            LOGGER.error(f"Failed to refresh JWKS from Keycloak: {exc}")
            raise HTTPException(
                status_code=HTTP_401_UNAUTHORIZED,
                detail="Authentication server unavailable.",
            )

        if kid in self._jwks_cache:
            return self._jwks_cache[kid]

        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail=f"No public key found for kid: {kid}",
        )

    async def _refresh_jwks(self):
        """Récupère les JWKS de Keycloak de manière non-bloquante pour l'event loop."""
        keycloak_url = self._env.get(EnvKey.WIKI_KEYCLOAK_URL, "")
        keycloak_url = keycloak_url.rstrip("/")
        jwks_url = f"{keycloak_url}/protocol/openid-connect/certs"

        response = await self._client.get(jwks_url)
        if response.status_code != 200:
            raise Exception(
                f"Keycloak certs endpoint returned status {response.status_code}"
            )

        jwks = response.json()
        new_cache = {}

        for jwk in jwks.get("keys", []):
            jwk_kid = jwk.get("kid")
            if not jwk_kid:
                continue

            alg = jwk.get("alg")
            if not alg:
                kty = jwk.get("kty")
                if kty == "RSA":
                    alg = "RS256"
                elif kty == "EC":
                    alg = "ES256"
                elif kty == "OKP":
                    alg = "EdDSA"
                else:
                    continue

            algo_impl = get_default_algorithms().get(alg)
            if not algo_impl:
                continue

            try:
                jwk_json = orjson.dumps(jwk).decode("utf-8")
                public_key = algo_impl.from_jwk(jwk_json)
                new_cache[jwk_kid] = public_key
            except Exception as exc:
                LOGGER.warning(f"Could not build key for kid {jwk_kid}: {exc}")

        self._jwks_cache.update(new_cache)

    async def oauth2_introspect(self, oauth2_token: str) -> dict:
        await asyncio.sleep(0.1)
        return {
            "username": "Tester",
            "roles": ["employee", "manager"],
            "groups": ["group1", "group2"],
            "scopes": ["openid", "email"],
        }
