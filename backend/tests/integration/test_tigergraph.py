import pytest
from unittest.mock import MagicMock, patch
from app.core.config import settings
from app.integrations.tigergraph.client import TigerGraphClient
from app.integrations.tigergraph.service import TigerGraphService
from app.integrations.tigergraph.exceptions import (
    TigerGraphError,
    TigerGraphConnectionError,
    TigerGraphUpsertError,
)


def test_tigergraph_config_loading() -> None:
    """Verify TigerGraph settings are correctly loaded into Settings config."""
    assert hasattr(settings, "TIGERGRAPH_HOST")
    assert hasattr(settings, "TIGERGRAPH_GRAPH")
    assert settings.TIGERGRAPH_HOST is not None
    assert settings.TIGERGRAPH_GRAPH == "FraudGraph"


def test_tigergraph_service_initialization() -> None:
    """Verify TigerGraphService initializes with client dependency."""
    mock_client = MagicMock(spec=TigerGraphClient)
    service = TigerGraphService(client=mock_client)
    assert service.client == mock_client


def test_tigergraph_health_check_mocked() -> None:
    """Test health check returns True when connection echo succeeds."""
    mock_conn = MagicMock()
    mock_conn.echo.return_value = [{"message": "pong"}]
    
    client = TigerGraphClient()
    client._conn = mock_conn
    
    assert client.check_health() is True


def test_tigergraph_vertex_upsert_mocked() -> None:
    """Test vertex upsert calls pyTigerGraph upsertVertex correctly."""
    mock_conn = MagicMock()
    mock_conn.upsertVertex.return_value = 1

    client = TigerGraphClient()
    client._conn = mock_conn

    service = TigerGraphService(client=client)
    success = service.upsert_user("usr_001", name="Alice", created_at="2026-09-30T12:00:00Z")

    assert success is True
    mock_conn.upsertVertex.assert_called_once_with(
        "User", "usr_001", attributes={"name": "Alice", "created_at": "2026-09-30T12:00:00Z"}
    )


def test_tigergraph_relationship_upsert_mocked() -> None:
    """Test relationship creation calls pyTigerGraph upsertEdge correctly."""
    mock_conn = MagicMock()
    mock_conn.upsertEdge.return_value = 1

    client = TigerGraphClient()
    client._conn = mock_conn

    service = TigerGraphService(client=client)
    success = service.create_user_account_relationship("usr_001", "acc_100")

    assert success is True
    mock_conn.upsertEdge.assert_called_once_with(
        "User", "usr_001", "OWNS", "Account", "acc_100", attributes={}
    )


def test_tigergraph_upsert_error_handling() -> None:
    """Test custom TigerGraphUpsertError is raised when pyTigerGraph fails."""
    mock_conn = MagicMock()
    mock_conn.upsertVertex.side_effect = Exception("Database connection reset")

    client = TigerGraphClient()
    client._conn = mock_conn

    service = TigerGraphService(client=client)

    with pytest.raises(TigerGraphUpsertError) as exc_info:
        service.upsert_user("usr_error", name="Bob")

    assert "Vertex upsert failed" in str(exc_info.value)


@pytest.mark.asyncio
async def test_test_transaction_endpoint(async_client) -> None:
    """Test the dev endpoint /api/v1/graph/test-transaction with mocked service."""
    from app.main import app
    from app.integrations.tigergraph.service import get_tigergraph_service

    mock_svc = MagicMock()
    mock_svc.ingest_full_transaction.return_value = True
    app.dependency_overrides[get_tigergraph_service] = lambda: mock_svc
    try:
        response = await async_client.post(
            "/api/v1/graph/test-transaction",
            json={"transaction_id": "tx_mock_1", "amount": 100.0},
        )
        assert response.status_code == 201
        data = response.json()
        assert data["status"] == "success"
    finally:
        app.dependency_overrides.pop(get_tigergraph_service, None)
