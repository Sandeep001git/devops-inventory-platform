
import os
from typing import TypedDict


class DatabaseConfig(TypedDict):
    """Connection settings accepted by psycopg."""

    host: str
    port: int
    dbname: str
    user: str
    password: str
    sslmode: str


def get_database_config() -> DatabaseConfig:
    """Read database connection settings from environment variables."""
    required = (
        "POSTGRES_HOST",
        "POSTGRES_DB",
        "POSTGRES_USER",
        "POSTGRES_PASSWORD",
    )
    missing = [name for name in required if not os.getenv(name)]
    if missing:
        raise RuntimeError(
            f"Missing required database environment variables: {', '.join(missing)}"
        )

    try:
        port = int(os.getenv("POSTGRES_PORT", "5432"))
    except ValueError as exc:
        raise RuntimeError("POSTGRES_PORT must be an integer") from exc

    return {
        "host": os.environ["POSTGRES_HOST"],
        "port": port,
        "dbname": os.environ["POSTGRES_DB"],
        "user": os.environ["POSTGRES_USER"],
        "password": os.environ["POSTGRES_PASSWORD"],
	    "sslmode": os.getenv("POSTGRES_SSLMODE", "require"),
    }
