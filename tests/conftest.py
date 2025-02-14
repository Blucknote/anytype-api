"""Pytest configuration and fixtures"""

import os
import sys
from typing import AsyncGenerator

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from httpx import AsyncClient

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.clients.anytype import AnytypeClient
from app.core.config import Settings, get_settings
from app.main import app


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest.fixture(scope="session", autouse=True)
def test_settings() -> Settings:
    """Create test settings with environment variables from .env.test"""
    # Override the env_file in model_config for testing
    Settings.model_config["env_file"] = os.path.join(
        os.path.dirname(__file__), ".env.test"
    )
    return get_settings()


@pytest.fixture(scope="session")
def test_app(test_settings):
    """Create a FastAPI test application"""
    return app


@pytest_asyncio.fixture(scope="session")
async def test_client(test_app) -> AsyncGenerator[AsyncClient, None]:
    """Create a test client for the FastAPI application"""
    async with AsyncClient(base_url="http://test") as client:
        yield client


@pytest.fixture(scope="session")
def anytype_client(test_settings) -> AnytypeClient:
    """Create an instance of the AnytypeClient"""
    return AnytypeClient(
        base_url=str(test_settings.anytype_api_url),
        session_token=test_settings.anytype_session_token,
        app_key=test_settings.anytype_app_key,
    )
