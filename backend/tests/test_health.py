from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.core.errors import AppError, register_error_handlers


def test_health_retorna_ok(client: TestClient) -> None:
    response = client.get("/health")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["app"]
    assert body["environment"]


def test_app_error_usa_envelope_padrao() -> None:
    app = FastAPI()

    @app.get("/erro")
    def erro() -> None:
        raise AppError(code="exemplo", message="Mensagem de exemplo.")

    register_error_handlers(app)
    client = TestClient(app, raise_server_exceptions=False)

    response = client.get("/erro")

    assert response.status_code == 400
    assert response.json() == {
        "error": {
            "code": "exemplo",
            "message": "Mensagem de exemplo.",
            "details": None,
        }
    }
