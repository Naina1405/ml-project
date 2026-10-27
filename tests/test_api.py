import pytest
from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)

def test_api_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "online"

def test_list_tasks_endpoint():
    response = client.get("/tasks?user_id=test_user")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_list_memories_endpoint():
    response = client.get("/memory?user_id=test_user")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
