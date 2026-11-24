from copy import deepcopy

import pytest
from fastapi.testclient import TestClient

from src.app import app, activities

client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    original = deepcopy(activities)
    yield
    activities.clear()
    activities.update(original)


def test_github_skills_available():
    response = client.get("/activities")
    assert response.status_code == 200
    activity = response.json()["GitHub Skills"]
    assert activity["participants"] == []
    assert activity["max_participants"] > 0


def test_github_skills_signup_and_unregister():
    email = "student@example.test"
    url = "/activities/GitHub Skills"
    assert client.post(url + "/signup", params={"email": email}).status_code == 200
    assert email in client.get("/activities").json()["GitHub Skills"]["participants"]
    assert client.delete(url + "/unregister", params={"email": email}).status_code == 200
    assert email not in client.get("/activities").json()["GitHub Skills"]["participants"]


def test_github_skills_duplicate_prevented():
    email = "student@example.test"
    url = "/activities/GitHub Skills/signup"
    assert client.post(url, params={"email": email}).status_code == 200
    assert client.post(url, params={"email": email}).status_code == 400


def test_existing_activities_preserved():
    data = client.get("/activities").json()
    assert len(data) == 10
    assert {"Chess Club", "Programming Class", "Gym Class"} <= data.keys()
