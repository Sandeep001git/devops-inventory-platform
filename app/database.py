
from collections.abc import Generator
from contextlib import contextmanager
from typing import Any, cast

import psycopg
from psycopg import Connection

from app.config import get_database_config


@contextmanager
def get_connection() -> Generator[Connection, None, None]:
    """Yield a database connection and close it when finished."""
    database_config = cast(dict[str, Any], get_database_config())
    with psycopg.connect(**database_config) as connection:
        yield connection
