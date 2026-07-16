import logging

import pytest
from starlette.status import HTTP_403_FORBIDDEN

from app.core.exceptions.api_exception import ApiException
from app.models.security.auth_user import AuthenticatedUser
from app.security.access_granter import has_any_roles, has_role, has_roles

LOGGER = logging.getLogger("test_logger")


@pytest.fixture
def auth_user():
    return AuthenticatedUser(
        user_id="user-123",
        username="tester",
        email="tester@test.com",
        roles=["employee", "manager"],
        scopes=["openid"],
        groups=[],
    )


@pytest.mark.asyncio
async def test_decorator_has_role_success(auth_user):
    """Autorise l'accès si l'utilisateur possède le rôle unique requis."""

    @has_role(LOGGER, "test_resource", "manager")
    async def dummy_route(user: AuthenticatedUser):
        return "success"

    result = await dummy_route(auth_user)
    assert result == "success"


@pytest.mark.asyncio
async def test_decorator_has_role_forbidden(auth_user):
    """Lève une ApiException 403 si l'utilisateur n'a pas le rôle unique requis."""

    @has_role(LOGGER, "test_resource", "director")
    async def dummy_route(user: AuthenticatedUser):
        return "success"

    with pytest.raises(ApiException) as exc_info:
        await dummy_route(auth_user)

    assert exc_info.value.status_code == HTTP_403_FORBIDDEN


@pytest.mark.asyncio
async def test_decorator_has_roles_all_required_success(auth_user):
    """Autorise l'accès si l'utilisateur possède TOUS les rôles requis."""

    @has_roles(LOGGER, "test_resource", ["employee", "manager"])
    async def dummy_route(user: AuthenticatedUser):
        return "success"

    result = await dummy_route(auth_user)
    assert result == "success"


@pytest.mark.asyncio
async def test_decorator_has_roles_all_required_missing_one(auth_user):
    """Lève une ApiException 403 s'il manque au moins un rôle requis."""

    @has_roles(LOGGER, "test_resource", ["employee", "director"])
    async def dummy_route(user: AuthenticatedUser):
        return "success"

    with pytest.raises(ApiException) as exc_info:
        await dummy_route(auth_user)

    assert exc_info.value.status_code == HTTP_403_FORBIDDEN


@pytest.mark.asyncio
async def test_decorator_has_any_roles_one_matches(auth_user):
    """Autorise si au moins un rôle correspond (has_any_roles)."""

    @has_any_roles(LOGGER, "test_resource", ["director", "manager"])
    async def dummy_route(user: AuthenticatedUser):
        return "success"

    result = await dummy_route(auth_user)
    assert result == "success"


@pytest.mark.asyncio
async def test_decorator_has_any_roles_none_matches(auth_user):

    @has_any_roles(LOGGER, "test_resource", ["director", "admin"])
    async def dummy_route(user: AuthenticatedUser):
        return "success"

    with pytest.raises(ApiException) as exc_info:
        await dummy_route(auth_user)

    assert exc_info.value.status_code == HTTP_403_FORBIDDEN


@pytest.mark.asyncio
async def test_decorator_missing_authenticated_user_arg():

    @has_role(LOGGER, "test_resource", "manager")
    async def dummy_route(some_random_arg: str):
        return "success"

    with pytest.raises(ApiException) as exc_info:
        await dummy_route("not_a_user")

    assert exc_info.value.status_code == HTTP_403_FORBIDDEN
