from abc import ABC, abstractmethod

import orjson
from jwt.utils import base64url_decode

from app.models.security.auth_user import AuthenticatedUser


class AuthenticationManager(ABC):
    @abstractmethod
    def supports(self, token: str) -> bool: ...

    @abstractmethod
    async def authenticate(self, token: str) -> AuthenticatedUser: ...

    def is_jwt_token(self, token: str) -> bool:
        if len(token.split(".", 2)) == 3:
            header, _, _ = token.rsplit(".", 2)
        else:
            return False
        if header is None:
            return False
        try:
            jwt_header = orjson.loads(base64url_decode(header))
            return "kid" in jwt_header and "alg" in jwt_header
        except Exception:
            return False
