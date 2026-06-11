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


def test_health_reports_degraded_when_dependency_checks_fail(monkeypatch) -> None:
    async def database_error() -> bool:
        return False

    async def redis_ok() -> bool:
        return True

    async def storage_error() -> bool:
        return False

    monkeypatch.setattr(health_module, "check_database", database_error)
    monkeypatch.setattr(health_module, "check_redis", redis_ok)
    monkeypatch.setattr(health_module, "check_storage", storage_error)

    client = TestClient(app)
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "degraded",
        "services": {
            "app": "ok",
            "database": "error",
            "redis": "ok",
            "object_storage": "error",
        },
    }
