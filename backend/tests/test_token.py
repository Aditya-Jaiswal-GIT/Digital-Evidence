
def test_refresh_token_rotation(client):
    # Login
    login_response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "investigator_test@example.com",
            "password": "StrongTestPassword123"
        }
    )

    assert login_response.status_code == 200

    old_refresh_token = login_response.json()["refresh_token"]

    # Refresh
    refresh_response = client.post(
        "/api/v1/auth/refresh",
        json={
            "refresh_token": old_refresh_token
        }
    )

    assert refresh_response.status_code == 200

    new_tokens = refresh_response.json()

    new_refresh_token = new_tokens["refresh_token"]

    assert new_refresh_token != old_refresh_token
    assert "access_token" in new_tokens

    # Old refresh token must not work again
    old_token_response = client.post(
        "/api/v1/auth/refresh",
        json={
            "refresh_token": old_refresh_token
        }
    )

    assert old_token_response.status_code == 401


def test_logout(client):
    # Login
    login_response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "investigator_test@example.com",
            "password": "StrongTestPassword123"
        }
    )

    assert login_response.status_code == 200

    refresh_token = login_response.json()["refresh_token"]

    # Logout
    logout_response = client.post(
        "/api/v1/auth/logout",
        json={
            "refresh_token": refresh_token
        }
    )

    assert logout_response.status_code == 200

    # Refresh after logout must fail
    refresh_response = client.post(
        "/api/v1/auth/refresh",
        json={
            "refresh_token": refresh_token
        }
    )

    assert refresh_response.status_code == 401


def test_invalid_refresh_token(client):
    response = client.post(
        "/api/v1/auth/refresh",
        json={
            "refresh_token": "invalid_token_123456789012345"
        }
    )

    assert response.status_code == 401
