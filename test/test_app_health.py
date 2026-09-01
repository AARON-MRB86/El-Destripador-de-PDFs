from fastapi.testclient import TestClient

from app.main import app, create_app


def test_create_app_returns_fastapi_app():
    created = create_app()
    assert created is not None
    assert callable(created.get)


def test_health_endpoint_is_exposed():
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] in {"ok", "degraded"}
    assert "database" in payload
