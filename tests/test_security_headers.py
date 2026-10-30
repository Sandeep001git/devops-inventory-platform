
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_security_headers() -> None:
    response = client.get("/")

    assert response.status_code == 200
    assert response.headers["strict-transport-security"] == (
        "max-age=31536000; includeSubDomains"
    )
    assert response.headers["x-content-type-options"] == "nosniff"
    assert response.headers["x-frame-options"] == "DENY"
    assert response.headers["referrer-policy"] == (
        "strict-origin-when-cross-origin"
    )
    assert response.headers["content-security-policy"] == "default-src 'self'"
