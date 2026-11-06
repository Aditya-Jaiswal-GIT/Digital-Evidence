
def test_register_user(client):
    response = client.post(
        "/api/v1/auth/register",
        json={
            "full_name": "Test Investigator",
            "email": "investigator_test@example.com",
            "password": "StrongTestPassword123"
        }
    )

    assert response.status_code == 201

    data = response.json()

    assert data["email"] == "investigator_test@example.com"
    assert data["role"] == "investigator"
    assert "password_hash" not in data
    assert "password" not in data


def test_duplicate_registration(client):
    response = client.post(
        "/api/v1/auth/register",
        json={
            "full_name": "Test Investigator",
            "email": "investigator_test@example.com",
            "password": "StrongTestPassword123"
        }
    )

    assert response.status_code == 409


def test_login_success(client):
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "investigator_test@example.com",
            "password": "StrongTestPassword123"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


def test_login_wrong_password(client):
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "investigator_test@example.com",
            "password": "WrongPassword123"
        }
    )

    assert response.status_code == 401
