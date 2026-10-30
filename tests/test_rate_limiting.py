
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_create_item_rate_limit() -> None:
    payload = {
        "name": "Rate Limit Test",
        "description": "Testing API rate limiting",
        "quantity": 1,
    }

    for _ in range(5):
        response = client.post("/items", json=payload)
        assert response.status_code == 201

    response = client.post("/items", json=payload)

    assert response.status_code == 429
