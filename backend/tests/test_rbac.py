import os
from dotenv import load_dotenv
load_dotenv()

def test_protected_endpoint_without_token(client):
    response = client.get("/api/v1/users/me")

    assert response.status_code == 401


def test_protected_endpoint_with_valid_token(client):
    # Register a new test user
    import uuid

    email = f"rbac_{uuid.uuid4().hex}@example.com"
    password = "StrongTestPassword123"

    register_response = client.post(
        "/api/v1/auth/register",
        json={
            "full_name": "RBAC Test User",
            "email": email,
            "password": password
        }
    )

    assert register_response.status_code == 201

    # Login to obtain access token
    login_response = client.post(
        "/api/v1/auth/login",
        json={
            "email": email,
            "password": password
        }
    )

    assert login_response.status_code == 200

    access_token = login_response.json()["access_token"]

    # Access protected endpoint
    response = client.get(
        "/api/v1/users/me",
        headers={
            "Authorization": f"Bearer {access_token}"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["email"] == email
    assert data["role"] == "investigator"



def test_investigator_cannot_access_admin_user_list(client):
    import uuid

    email = f"investigator_{uuid.uuid4().hex}@example.com"
    password = "StrongTestPassword123"

    # Register investigator
    register_response = client.post(
        "/api/v1/auth/register",
        json={
            "full_name": "Investigator Test",
            "email": email,
            "password": password
        }
    )

    assert register_response.status_code == 201

    # Login
    login_response = client.post(
        "/api/v1/auth/login",
        json={
            "email": email,
            "password": password
        }
    )

    assert login_response.status_code == 200

    access_token = login_response.json()["access_token"]

    # Attempt to access admin-only endpoint
    response = client.get(
        "/api/v1/users",
        headers={
            "Authorization": f"Bearer {access_token}"
        }
    )

    assert response.status_code == 403




def test_admin_can_access_user_list(client):
    import os
    from dotenv import load_dotenv

    # Load environment variables from .env
    load_dotenv()

    admin_email = os.getenv("TEST_ADMIN_EMAIL")
    admin_password = os.getenv("TEST_ADMIN_PASSWORD")

    assert admin_email, "TEST_ADMIN_EMAIL is missing"
    assert admin_password, "TEST_ADMIN_PASSWORD is missing"

    # Step 1: Admin login
    login_response = client.post(
        "/api/v1/auth/login",
        json={
            "email": admin_email,
            "password": admin_password
        }
    )

    assert login_response.status_code == 200, (
        f"Admin login failed: {login_response.text}"
    )

    access_token = login_response.json()["access_token"]

    # Step 2: Access admin-only user management endpoint
    response = client.get(
        "/api/v1/users",
        headers={
            "Authorization": f"Bearer {access_token}"
        }
    )

    # Step 3: Debug response
    print("Users API status:", response.status_code)
    print("Users API error:", response.text)

    # Step 4: Validate response
    assert response.status_code == 200, (
        f"Admin could not access user list: {response.text}"
    )

    data = response.json()

    assert "users" in data
    assert "total" in data
    assert "page" in data
    assert "page_size" in data



def test_invalid_access_token(client):
    response = client.get(
        "/api/v1/users/me",
        headers={
            "Authorization": "Bearer invalid.token.value"
        }
    )

    assert response.status_code == 401




def test_expired_access_token(client):
    import jwt
    from datetime import datetime, timedelta, timezone
    from app.core.config import settings

    now = datetime.now(timezone.utc)

    expired_token = jwt.encode(
        {
            "sub": "507f1f77bcf86cd799439011",
            "role": "investigator",
            "type": "access",
            "jti": "expired-test-token",
            "iat": now - timedelta(minutes=10),
            "exp": now - timedelta(minutes=5)
        },
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )

    response = client.get(
        "/api/v1/users/me",
        headers={
            "Authorization": f"Bearer {expired_token}"
        }
    )

    assert response.status_code == 401

