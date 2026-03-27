from fastapi.testclient import TestClient

from src.api import app


client = TestClient(app)


def test_health_endpoint() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_tasks_endpoint() -> None:
    response = client.get("/tasks")
    assert response.status_code == 200
    body = response.json()
    assert len(body["tasks"]) == 3
    assert "action_schema" in body
