from typing import List

from fastapi import HTTPException, Request, status
from fastapi.security import HTTPBearer

from app.models.security.auth_user import AuthenticatedUser
from app.security.managers.authentication_manager import AuthenticationManager


class AuthenticationProvider(HTTPBearer):
    def __init__(self, managers: List[AuthenticationManager], auto_error: bool = True):
        super().__init__(auto_error=auto_error)
        self.managers = managers

    async def __call__(self, request: Request) -> AuthenticatedUser:
        credentials = await super().__call__(request)

        if not credentials:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not authenticated",
            )

        if credentials.scheme.lower() != "bearer":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication scheme. Bearer token required.",
            )

        token = credentials.credentials

        for manager in self.managers:
            if manager.supports(token):
                return await manager.authenticate(token)

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No suitable authentication manager found for this token.",
        )
