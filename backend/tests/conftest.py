import pytest
from typing import AsyncGenerator
from httpx import AsyncClient, ASGITransport
from app.main import app


@pytest.fixture
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    """Fixture to provide an async HTTP client for FastAPI testing."""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as client:
        yield client
