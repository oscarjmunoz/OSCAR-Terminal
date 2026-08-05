from fastapi.testclient import TestClient

from app.main import app
from app.config.settings import settings

client = TestClient(app)


def test_health_contracts():

    for path in ("/health", "/api/v1/health"):

        response = client.get(path)

        assert response.status_code == 200

        assert response.json() == {
            "status": "ok",
            "service": settings.APP_NAME,
            "version": settings.APP_VERSION,
        }