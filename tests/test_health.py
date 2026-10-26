from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_endpoint_returns_ok() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_readiness_endpoint_returns_ready() -> None:
    response = client.get("/ready")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ready",
        "database": "ok",
    }


def test_readiness_endpoint_returns_503_when_database_fails() -> None:
    with patch(
        "app.main.get_connection",
        side_effect=__import__("psycopg").OperationalError(
            "simulated database failure"
        ),
    ):
        response = client.get("/ready")

    assert response.status_code == 503
    assert response.json() == {
        "detail": "Database is unavailable",
    }


def test_unknown_endpoint_return_not_found() -> None:
    response = client.get("/does-not-exist")
    assert response.status_code == 404

def test_root_endpoint_returns_service_information() -> None:
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {
        "service": "DevOps Inventory API",
        "health": "/health",
        "readiness": "/ready",
    }

def test_create_inventory_item() -> None:
    response = client.post(
        "/items",
        json={
            "name": "Keyboard",
            "description": "Mechanical keyboard",
            "quantity": 10,
        },
    )

    assert response.status_code == 201
    body = response.json()
    assert body["id"] >= 1
    assert body["name"] == "Keyboard"
    assert body["description"] == "Mechanical keyboard"
    assert body["quantity"] == 10


def test_create_item_rejects_negative_quantity() -> None:
    response = client.post(
        "/items",
        json={"name": "Keyboard", "quantity": -1},
    )

    assert response.status_code == 422

def test_list_inventory_items() -> None:
    client.post(
        "/items",
        json={"name": "Mouse", "quantity": 5},
    )

    response = client.get("/items")

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["name"] == "Mouse"
    assert response.json()[0]["quantity"] == 5

def test_get_inventory_item_by_id() -> None:

    created = client.post(
        "/items",
        json={"name": "Mouse", "quantity": 5},
    )
    item_id = created.json()["id"]

    response = client.get(f"/items/{item_id}")

    assert response.status_code == 200
    assert response.json()["id"] == item_id
    assert response.json()["name"] == "Mouse"


def test_get_missing_inventory_item_returns_404() -> None:

    response = client.get("/items/-1")

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Inventory item not found"
    }

def test_delete_inventory_item() -> None:

    created = client.post(
        "/items",
        json={"name": "Mouse", "quantity": 5},
    )
    item_id = created.json()["id"]

    response = client.delete(f"/items/{item_id}")

    assert response.status_code == 204
    assert client.get(f"/items/{item_id}").status_code == 404


def test_delete_missing_inventory_item_returns_404() -> None:

    response = client.delete("/items/-1")

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Inventory item not found"
    }

def test_update_inventory_item() -> None:

    created = client.post(
        "/items",
        json={"name": "Mouse", "quantity": 5},
    )
    item_id = created.json()["id"]

    response = client.put(
        f"/items/{item_id}",
        json={
            "name": "Wireless Mouse",
            "description": "Bluetooth mouse",
            "quantity": 8,
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        "id": item_id,
        "name": "Wireless Mouse",
        "description": "Bluetooth mouse",
        "quantity": 8,
    }


def test_update_missing_inventory_item_returns_404() -> None:

    response = client.put(
        "/items/-1",
        json={"name": "Mouse", "quantity": 5},
    )

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Inventory item not found"
    }

def test_patch_inventory_item_changes_only_supplied_fields() -> None:

    created = client.post(
        "/items",
        json={
            "name": "Mouse",
            "description": "Wired mouse",
            "quantity": 5,
        },
    )
    item_id = created.json()["id"]

    response = client.patch(
        f"/items/{item_id}",
        json={"quantity": 8},
    )

    assert response.status_code == 200
    assert response.json() == {
        "id": item_id,
        "name": "Mouse",
        "description": "Wired mouse",
        "quantity": 8,
    }

def test_patch_rejects_null_name() -> None:

    created = client.post(
        "/items",
        json={"name": "Mouse", "quantity": 5},
    )
    item_id = created.json()["id"]

    response = client.patch(
        f"/items/{item_id}",
        json={"name": None},
    )

    assert response.status_code == 422
    assert client.get(f"/items/{item_id}").json()["name"] == "Mouse"