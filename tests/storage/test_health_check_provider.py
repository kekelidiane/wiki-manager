from unittest.mock import AsyncMock, MagicMock

import pytest

from app.storage.rds.datastore.health.health_check_provider import HealthCheckProvider


@pytest.mark.asyncio
async def test_health_check_success():
    mock_connection = AsyncMock()
    mock_connection.fetchval.return_value = 1

    mock_transaction = AsyncMock()
    mock_connection.transaction = MagicMock(return_value=mock_transaction)

    mock_pool = MagicMock()
    mock_pool.acquire.return_value.__aenter__.return_value = mock_connection

    mock_db_manager = MagicMock()
    mock_db_manager.connection_pool = mock_pool

    provider = HealthCheckProvider(database_manager=mock_db_manager)
    result = await provider.health_check()

    assert result is True
    mock_connection.fetchval.assert_called_once_with("SELECT 1")


@pytest.mark.asyncio
async def test_health_check_failure():
    mock_connection = AsyncMock()
    mock_connection.fetchval.return_value = None

    mock_transaction = AsyncMock()
    mock_connection.transaction = MagicMock(return_value=mock_transaction)

    mock_pool = MagicMock()
    mock_pool.acquire.return_value.__aenter__.return_value = mock_connection

    mock_db_manager = MagicMock()
    mock_db_manager.connection_pool = mock_pool

    provider = HealthCheckProvider(database_manager=mock_db_manager)
    result = await provider.health_check()

    assert result is False


@pytest.mark.asyncio
async def test_health_check_exception():
    mock_connection = AsyncMock()
    mock_connection.fetchval.side_effect = Exception("Connection lost")

    mock_transaction = AsyncMock()
    mock_connection.transaction = MagicMock(return_value=mock_transaction)

    mock_pool = MagicMock()
    mock_pool.acquire.return_value.__aenter__.return_value = mock_connection

    mock_db_manager = MagicMock()
    mock_db_manager.connection_pool = mock_pool

    provider = HealthCheckProvider(database_manager=mock_db_manager)
    result = await provider.health_check()

    assert result is False
