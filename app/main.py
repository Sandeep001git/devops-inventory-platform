import logging
from typing import cast

import psycopg
from fastapi import FastAPI, HTTPException, Request, status
from psycopg import sql
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from starlette.types import ExceptionHandler

from app.database import get_connection
from app.schemas import InventoryItemCreate, InventoryItemUpdate

app = FastAPI(
    title="DevOps Inventory API",
    description="An inventory management API built as a DevOps portfolio project.",
    version="0.1.0",
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)

logger = logging.getLogger("inventory_api")

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(
    RateLimitExceeded,
    cast(ExceptionHandler, _rate_limit_exceeded_handler),
)

@app.middleware("http")
async def add_security_headers(request, call_next):
    response = await call_next(request)

    response.headers["Strict-Transport-Security"] = (
        "max-age=31536000; includeSubDomains"
    )
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Content-Security-Policy"] = "default-src 'self'"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

    return response

@app.get("/")
def root() -> dict[str, str]:
    """Provide basic API information."""
    return {
        "service": "DevOps Inventory API",
        "health": "/health",
        "readiness": "/ready",
    }

@app.get("/health")
def health_check() -> dict[str, str]:
    """Report whether the API process is responding."""
    return {"status": "ok"}

@app.get("/ready")
def readiness_check() -> dict[str, str]:
    """Report whether the API can access PostgreSQL."""
    try:
        with get_connection() as connection, connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            row = cursor.fetchone()
    except psycopg.Error as exc:
        logger.exception("Database readiness check failed")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database is unavailable",
        ) from exc

    if row is None or row[0] != 1:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database is not ready"
        )

    return { "status": "ready", "database": "ok"}

@app.get("/items")
def list_items() -> list[dict[str, object]]:
    """Return all inventory items."""
    with get_connection() as connection, connection.cursor() as cursor:
        cursor.execute(
            """
                SELECT id , name , description , quantity
                FROM inventory_items
                ORDER BY id
                """
        )
        rows = cursor.fetchall()

    return [
        {

            "id":row[0],
            "name": row[1],
            "description": row[2],
            "quantity": row[3],
        }
        for row in rows
    ]

@app.post("/items", status_code=status.HTTP_201_CREATED)
@limiter.limit("5/minute")
def create_item(
    request: Request,
    item: InventoryItemCreate,
) -> dict[str, object]:
    """Create an inventory item in PostgreSQL."""
    with get_connection() as connection, connection.cursor() as cursor:
        cursor.execute(
            """
                INSERT INTO inventory_items (name, description, quantity)
                VALUES (%s, %s, %s)
                RETURNING id, name, description, quantity
                """,
            (item.name, item.description, item.quantity),
        )
        row = cursor.fetchone()

        if row is None:
            raise RuntimeError("Insert returned no inventory item")

        logger.info("Inventory item created: id=%s", row[0])

    return {
        "id": row[0],
        "name": row[1],
        "description": row[2],
        "quantity": row[3],
    }

@app.get("/items/{item_id}")
def get_item(item_id: int) -> dict[str, object]:
    """Return one inventory item from PostgreSQL."""
    with get_connection() as connection, connection.cursor() as cursor:
        cursor.execute(
            """
                SELECT id, name, description, quantity
                FROM inventory_items
                WHERE id = %s
                """,
            (item_id,),
        )
        row = cursor.fetchone()

    if row is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Inventory item not found",
        )

    return {
        "id": row[0],
        "name": row[1],
        "description": row[2],
        "quantity": row[3],
    }

@app.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_item(item_id: int) -> None:
    """Delete an inventory item from PostgreSQL."""
    with get_connection() as connection, connection.cursor() as cursor:
        cursor.execute(
            """
                DELETE FROM inventory_items
                WHERE id = %s
                RETURNING id
                """,
            (item_id,),
        )
        deleted_row = cursor.fetchone()
        if deleted_row is not None:
            logger.info("Inventory item deleted: id=%s", deleted_row[0])

    if deleted_row is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Inventory item not found",
        )

@app.put("/items/{item_id}")
def update_item(
    item_id: int,
    updated_item: InventoryItemCreate,
) -> dict[str, object]:
    """Replace an existing inventory item in PostgreSQL."""
    with get_connection() as connection, connection.cursor() as cursor:
        cursor.execute(
            """
                UPDATE inventory_items
                SET name = %s,
                    description = %s,
                    quantity = %s,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = %s
                RETURNING id, name, description, quantity
                """,
            (
                updated_item.name,
                updated_item.description,
                updated_item.quantity,
                item_id,
            ),
        )
        row = cursor.fetchone()

    if row is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Inventory item not found",
        )

    return {
        "id": row[0],
        "name": row[1],
        "description": row[2],
        "quantity": row[3],
    }

@app.patch("/items/{item_id}")
def patch_item(
    item_id: int,
    changes: InventoryItemUpdate,
) -> dict[str, object]:
    """Update only supplied inventory fields in PostgreSQL."""
    updated_fields = changes.model_dump(exclude_unset=True)

    if not updated_fields:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one field must be provided",
        )

    assignments = sql.SQL(", ").join(
        sql.SQL("{} = %s").format(sql.Identifier(field))
        for field in updated_fields
    )
    values = list(updated_fields.values())
    values.append(item_id)

    query = sql.SQL(
        """
        UPDATE inventory_items
        SET {},
            updated_at = CURRENT_TIMESTAMP
        WHERE id = %s
        RETURNING id, name, description, quantity
        """
    ).format(assignments)

    with get_connection() as connection, connection.cursor() as cursor:
        cursor.execute(query, values)
        row = cursor.fetchone()

    if row is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Inventory item not found",
        )

    return {
        "id": row[0],
        "name": row[1],
        "description": row[2],
        "quantity": row[3],
    }
