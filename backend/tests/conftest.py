
import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture(scope="session")
def client():
    with TestClient(app) as test_client:
        yield test_client

import uuid
import pytest

@pytest.fixture
def registered_user(client):
    email = f"test_{uuid.uuid4().hex}@example.com"
    password = "StrongTestPassword123"

    response = client.post(
        "/api/v1/auth/register",
        json={
            "full_name": "Test Investigator",
            "email": email,
            "password": password
        }
    )

    assert response.status_code == 201, response.text

    return {
        "email": email,
        "password": password
    }