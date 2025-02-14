"""Pytest configuration and fixtures"""
import os
import sys
from typing import AsyncGenerator

import pytest
from httpx import AsyncClient

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.main import app, AnytypeClient
from app.main import app, AnytypeClient


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest.fixture(scope="session")
async def test_client() -> AsyncGenerator[AsyncClient, None]:
    """
    Create a test client for the FastAPI application.
    """
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client


@pytest.fixture(scope="session")
def anytype_client() -> AnytypeClient:
    """
    Create an instance of the AnytypeClient.
    """
    # Mock environment variables for testing
    os.environ["ANYTYPE_API_URL"] = "https://test.anytype.io"
    os.environ["ANYTYPE_SESSION_TOKEN"] = "test_session_token"
    os.environ["ANYTYPE_APP_KEY"] = "test_app_key"
    return AnytypeClient()