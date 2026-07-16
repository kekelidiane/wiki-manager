import functools
import logging
from typing import List, Optional

from starlette.status import HTTP_403_FORBIDDEN

from app.core.exceptions.api_exception import ApiErrorsCode, ApiException
from app.models.security.auth_user import AuthenticatedUser


def _extract_authenticated_user(*args, **kwargs) -> Optional[AuthenticatedUser]:
    """Extrait l'AuthenticatedUser parmi les arguments positionnels ou nommés."""
    for arg in args:
        if isinstance(arg, AuthenticatedUser):
            return arg
    for val in kwargs.values():
        if isinstance(val, AuthenticatedUser):
            return val
    return None


def has_role(logger: logging.Logger, resource: str, role: str):
    def inner(f):
        @functools.wraps(f)
        async def __wrap__(*args, **kwargs):
            auth_user = _extract_authenticated_user(*args, **kwargs)

            if auth_user is None:
                logger.error(
                    f"function call: {f.__name__} denied for resource {resource}. "
                    f"No authenticated user found in signature."
                )
                raise ApiException(
                    status_code=HTTP_403_FORBIDDEN,
                    error_code=ApiErrorsCode.RESOURCE_ACCESS_DENIED,
                    message="resource access denied",
                )

            if auth_user.has_role(role):
                return await f(*args, **kwargs)

            logger.error(
                f"function call: {f.__name__} denied for resource: {resource} "
                f"and user: {auth_user.username}."
            )
            raise ApiException(
                status_code=HTTP_403_FORBIDDEN,
                error_code=ApiErrorsCode.RESOURCE_ACCESS_DENIED,
                message="resource access denied",
            )

        return __wrap__

    return inner


def has_roles(logger: logging.Logger, resource: str, roles: List[str]):
    def inner(f):
        @functools.wraps(f)
        async def __wrap__(*args, **kwargs):
            auth_user = _extract_authenticated_user(*args, **kwargs)

            if auth_user is None:
                logger.error(
                    f"function call: {f.__name__} denied for resource {resource}. "
                    f"No authenticated user found in signature."
                )
                raise ApiException(
                    status_code=HTTP_403_FORBIDDEN,
                    error_code=ApiErrorsCode.RESOURCE_ACCESS_DENIED,
                    message="resource access denied",
                )

            all_match = all(auth_user.has_role(r) for r in roles)

            if all_match:
                return await f(*args, **kwargs)

            logger.error(
                f"function call: {f.__name__} denied for resource: {resource} "
                f"and user: {auth_user.username} (missing some roles)."
            )
            raise ApiException(
                status_code=HTTP_403_FORBIDDEN,
                error_code=ApiErrorsCode.RESOURCE_ACCESS_DENIED,
                message="resource access denied",
            )

        return __wrap__

    return inner


def has_any_roles(logger: logging.Logger, resource: str, roles: List[str]):
    def inner(f):
        @functools.wraps(f)
        async def __wrap__(*args, **kwargs):
            auth_user = _extract_authenticated_user(*args, **kwargs)

            if auth_user is None:
                logger.error(
                    f"[{f.__name__}]: resource: {resource} access denied. "
                    f"No authenticated user found in signature."
                )
                raise ApiException(
                    status_code=HTTP_403_FORBIDDEN,
                    error_code=ApiErrorsCode.RESOURCE_ACCESS_DENIED,
                    message="resource access denied",
                )

            any_match = any(auth_user.has_role(r) for r in roles)

            if any_match:
                return await f(*args, **kwargs)

            logger.error(
                f"function call: {f.__name__} denied for resource: {resource} "
                f"and user: {auth_user.username} (missing all requested roles)."
            )
            raise ApiException(
                status_code=HTTP_403_FORBIDDEN,
                error_code=ApiErrorsCode.RESOURCE_ACCESS_DENIED,
                message="resource access denied",
            )

        return __wrap__

    return inner
