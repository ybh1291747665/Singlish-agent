from fastapi.testclient import TestClient

from singlish_agent_api.main import app


def test_health_returns_app_status() -> None:
    with TestClient(app) as client:
        response = client.get("/health")
        body = response.json()

    assert response.status_code == 200
    assert body["services"]["app"] == "ok"
    assert body["status"] in {"ok", "degraded"}
