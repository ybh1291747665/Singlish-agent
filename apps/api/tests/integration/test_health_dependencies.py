from fastapi.testclient import TestClient

import singlish_agent_api.api.routes.health as health_module
from singlish_agent_api.main import app


def test_health_reports_all_service_checks(monkeypatch) -> None:
    async def ok() -> bool:
        return True

    monkeypatch.setattr(health_module, "check_database", ok)
    monkeypatch.setattr(health_module, "check_redis", ok)
    monkeypatch.setattr(health_module, "check_storage", ok)

    client = TestClient(app)
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "services": {
            "app": "ok",
            "database": "ok",
            "redis": "ok",
            "object_storage": "ok",
        },
    }
