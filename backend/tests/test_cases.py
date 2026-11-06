
import os
import uuid

import pytest
from dotenv import load_dotenv

from bson import ObjectId


load_dotenv()


# --------------------------------------------------
# FIXTURE 1: ADMIN AUTHENTICATION
# --------------------------------------------------

@pytest.fixture(scope="module")
def admin_token(client):

    email = os.getenv("TEST_ADMIN_EMAIL")
    password = os.getenv("TEST_ADMIN_PASSWORD")

    assert email, "TEST_ADMIN_EMAIL is missing"
    assert password, "TEST_ADMIN_PASSWORD is missing"

    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": email,
            "password": password
        }
    )

    assert response.status_code == 200, response.text

    return response.json()["access_token"]


# --------------------------------------------------
# FIXTURE 2: AUTHORIZATION HEADERS
# --------------------------------------------------

@pytest.fixture(scope="module")
def admin_headers(admin_token):

    return {
        "Authorization": f"Bearer {admin_token}"
    }


# --------------------------------------------------
# FIXTURE 3: CREATE A TEST CASE
# --------------------------------------------------

@pytest.fixture
def admin_case(client, admin_headers):

    response = client.post(
        "/api/v1/cases/",
        headers=admin_headers,
        json={
            "title": f"Test Forensic Case {uuid.uuid4().hex[:8]}",
            "description": (
                "Testing digital evidence authenticity "
                "and forensic investigation."
            ),
            "case_type": "Image Forensics",
            "priority": "high"
        }
    )

    assert response.status_code == 201, response.text

    return response.json()


# --------------------------------------------------
# TEST 1: CREATE CASE
# --------------------------------------------------

def test_create_case(admin_case):

    assert admin_case["id"]
    assert admin_case["case_number"].startswith("CASE-")
    assert admin_case["title"]
    assert admin_case["status"] == "open"
    assert admin_case["priority"] == "high"

    assert "organization_id" in admin_case
    assert "created_by" in admin_case


# --------------------------------------------------
# TEST 2: LIST CASES
# --------------------------------------------------

def test_list_cases(client, admin_headers, admin_case):

    response = client.get(
        "/api/v1/cases/?page=1&page_size=10",
        headers=admin_headers
    )

    assert response.status_code == 200

    data = response.json()

    assert "cases" in data
    assert "total" in data
    assert "page" in data
    assert "page_size" in data

    case_ids = [case["id"] for case in data["cases"]]

    assert admin_case["id"] in case_ids


# --------------------------------------------------
# TEST 3: VIEW SINGLE CASE
# --------------------------------------------------

def test_view_case(client, admin_headers, admin_case):

    response = client.get(
        f"/api/v1/cases/{admin_case['id']}",
        headers=admin_headers
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == admin_case["id"]
    assert data["case_number"] == admin_case["case_number"]
    assert data["title"] == admin_case["title"]


# --------------------------------------------------
# TEST 4: UPDATE CASE DETAILS
# --------------------------------------------------

def test_update_case(client, admin_headers, admin_case):

    response = client.patch(
        f"/api/v1/cases/{admin_case['id']}",
        headers=admin_headers,
        json={
            "title": "Updated Forensic Investigation",
            "priority": "critical"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["title"] == "Updated Forensic Investigation"
    assert data["priority"] == "critical"


# --------------------------------------------------
# TEST 5: CHANGE CASE STATUS
# --------------------------------------------------

def test_change_case_status(client, admin_headers, admin_case):

    response = client.patch(
        f"/api/v1/cases/{admin_case['id']}/status",
        headers=admin_headers,
        json={
            "status": "in_progress"
        }
    )

    assert response.status_code == 200

    assert response.json()["status"] == "in_progress"


# --------------------------------------------------
# TEST 6: ASSIGN INVESTIGATOR
# --------------------------------------------------

def test_assign_investigator(
    client,
    admin_headers,
    admin_case
):

    investigator_id = os.getenv("TEST_INVESTIGATOR_ID")

    if not investigator_id:
        pytest.skip("TEST_INVESTIGATOR_ID is not configured")

    assert ObjectId.is_valid(investigator_id)

    response = client.post(
        f"/api/v1/cases/{admin_case['id']}/assign",
        headers=admin_headers,
        json={
            "user_id": investigator_id
        }
    )

    assert response.status_code == 200, response.text

    assigned_ids = response.json()["assigned_investigators"]

    assert investigator_id in assigned_ids


# --------------------------------------------------
# TEST 7: LIST ASSIGNED INVESTIGATORS
# --------------------------------------------------

def test_list_case_investigators(
    client,
    admin_headers,
    admin_case
):

    investigator_id = os.getenv("TEST_INVESTIGATOR_ID")

    if not investigator_id:
        pytest.skip("TEST_INVESTIGATOR_ID is not configured")

    # Assign investigator first
    assign_response = client.post(
        f"/api/v1/cases/{admin_case['id']}/assign",
        headers=admin_headers,
        json={"user_id": investigator_id}
    )

    assert assign_response.status_code == 200

    # Retrieve investigators
    response = client.get(
        f"/api/v1/cases/{admin_case['id']}/investigators",
        headers=admin_headers
    )

    assert response.status_code == 200

    data = response.json()

    assert investigator_id in data["assigned_investigators"]
    assert data["total"] >= 1


# --------------------------------------------------
# TEST 8: REMOVE INVESTIGATOR
# --------------------------------------------------

def test_remove_investigator(
    client,
    admin_headers,
    admin_case
):

    investigator_id = os.getenv("TEST_INVESTIGATOR_ID")

    if not investigator_id:
        pytest.skip("TEST_INVESTIGATOR_ID is not configured")

    # Assign investigator first
    assign_response = client.post(
        f"/api/v1/cases/{admin_case['id']}/assign",
        headers=admin_headers,
        json={"user_id": investigator_id}
    )

    assert assign_response.status_code == 200

    # Remove investigator
    response = client.delete(
        f"/api/v1/cases/{admin_case['id']}/assign/{investigator_id}",
        headers=admin_headers
    )

    assert response.status_code == 200

    assigned_ids = response.json()["assigned_investigators"]

    assert investigator_id not in assigned_ids


# --------------------------------------------------
# TEST 9: CLOSE CASE
# --------------------------------------------------

def test_close_case(client, admin_headers, admin_case):

    response = client.patch(
        f"/api/v1/cases/{admin_case['id']}/close",
        headers=admin_headers
    )

    assert response.status_code == 200

    assert response.json()["status"] == "closed"


# --------------------------------------------------
# TEST 10: ARCHIVE CLOSED CASE
# --------------------------------------------------

def test_archive_case(client, admin_headers, admin_case):

    # First close the case
    close_response = client.patch(
        f"/api/v1/cases/{admin_case['id']}/close",
        headers=admin_headers
    )

    assert close_response.status_code == 200

    # Then archive it
    archive_response = client.patch(
        f"/api/v1/cases/{admin_case['id']}/archive",
        headers=admin_headers
    )

    assert archive_response.status_code == 200

    data = archive_response.json()

    assert data["is_archived"] is True
    assert data["case_id"] == admin_case["id"]


# --------------------------------------------------
# TEST 11: UNAUTHENTICATED CASE LIST
# --------------------------------------------------

def test_case_list_without_token(client):

    response = client.get("/api/v1/cases/")

    assert response.status_code == 401


# --------------------------------------------------
# TEST 12: UNAUTHENTICATED CASE CREATION
# --------------------------------------------------

def test_create_case_without_token(client):

    response = client.post(
        "/api/v1/cases/",
        json={
            "title": "Unauthorized Test Case",
            "description": "Testing unauthorized case creation.",
            "case_type": "Image Forensics",
            "priority": "medium"
        }
    )

    assert response.status_code == 401


# --------------------------------------------------
# TEST 13: INVALID CASE ID
# --------------------------------------------------

def test_view_invalid_case_id(client, admin_headers):

    response = client.get(
        "/api/v1/cases/invalid_case_id",
        headers=admin_headers
    )

    assert response.status_code == 404


# --------------------------------------------------
# TEST 14: NON-EXISTENT CASE
# --------------------------------------------------

def test_view_nonexistent_case(client, admin_headers):

    fake_case_id = str(ObjectId())

    response = client.get(
        f"/api/v1/cases/{fake_case_id}",
        headers=admin_headers
    )

    assert response.status_code == 404


# --------------------------------------------------
# TEST 15: INVALID PAGINATION
# --------------------------------------------------

def test_invalid_case_pagination(client, admin_headers):

    response = client.get(
        "/api/v1/cases/?page=0&page_size=10",
        headers=admin_headers
    )

    assert response.status_code == 422


# --------------------------------------------------
# TEST 16: INVALID CASE PRIORITY
# --------------------------------------------------

def test_invalid_case_priority(client, admin_headers):

    response = client.post(
        "/api/v1/cases/",
        headers=admin_headers,
        json={
            "title": "Invalid Priority Test",
            "description": "Testing invalid case priority validation.",
            "case_type": "Image Forensics",
            "priority": "super_urgent"
        }
    )

    assert response.status_code == 422


# --------------------------------------------------
# TEST 17: INVALID CASE STATUS
# --------------------------------------------------

def test_invalid_case_status(client, admin_headers, admin_case):

    response = client.patch(
        f"/api/v1/cases/{admin_case['id']}/status",
        headers=admin_headers,
        json={
            "status": "unknown_status"
        }
    )

    assert response.status_code == 422
