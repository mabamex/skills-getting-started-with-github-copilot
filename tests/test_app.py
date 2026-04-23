import copy
import pytest
from fastapi.testclient import TestClient

import app as app_module

client = TestClient(app_module.app)

# Snapshot of the original activities state for resetting between tests
_original_activities = copy.deepcopy(app_module.activities)


@pytest.fixture(autouse=True)
def reset_activities():
    """Restore the in-memory activities dict to its original state before each test."""
    app_module.activities.clear()
    app_module.activities.update(copy.deepcopy(_original_activities))
    yield


# ---------------------------------------------------------------------------
# GET /activities
# ---------------------------------------------------------------------------

def test_get_activities_returns_all():
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 9


def test_get_activities_has_required_fields():
    response = client.get("/activities")
    assert response.status_code == 200
    for activity in response.json().values():
        assert "description" in activity
        assert "schedule" in activity
        assert "max_participants" in activity
        assert "participants" in activity


# ---------------------------------------------------------------------------
# POST /activities/{activity_name}/signup
# ---------------------------------------------------------------------------

def test_signup_success():
    response = client.post(
        "/activities/Chess Club/signup",
        params={"email": "newstudent@mergington.edu"},
    )
    assert response.status_code == 200
    assert "newstudent@mergington.edu" in app_module.activities["Chess Club"]["participants"]


def test_signup_activity_not_found():
    response = client.post(
        "/activities/Nonexistent Club/signup",
        params={"email": "test@mergington.edu"},
    )
    assert response.status_code == 404


def test_signup_already_registered():
    response = client.post(
        "/activities/Chess Club/signup",
        params={"email": "michael@mergington.edu"},
    )
    assert response.status_code == 400


# ---------------------------------------------------------------------------
# DELETE /activities/{activity_name}/signup
# ---------------------------------------------------------------------------

def test_unregister_success():
    response = client.delete(
        "/activities/Chess Club/signup",
        params={"email": "michael@mergington.edu"},
    )
    assert response.status_code == 200
    assert "michael@mergington.edu" not in app_module.activities["Chess Club"]["participants"]


def test_unregister_activity_not_found():
    response = client.delete(
        "/activities/Nonexistent Club/signup",
        params={"email": "michael@mergington.edu"},
    )
    assert response.status_code == 404


def test_unregister_email_not_found():
    response = client.delete(
        "/activities/Chess Club/signup",
        params={"email": "ghost@mergington.edu"},
    )
    assert response.status_code == 404
