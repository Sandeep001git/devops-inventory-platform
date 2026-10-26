
import pytest
from psycopg import sql

from app.database import get_connection


@pytest.fixture(autouse=True)
def isolate_inventory_items() -> None:
    """Clear the dedicated test table before each test."""
    with get_connection() as connection, connection.cursor() as cursor:
        cursor.execute(
            sql.SQL("TRUNCATE TABLE {} RESTART IDENTITY").format(
                sql.Identifier("inventory_items")
            )
        )