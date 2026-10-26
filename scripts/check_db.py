
import psycopg

from app.config import get_database_config


def main() -> None:
    """Verify that Python can connect to PostgreSQL."""
    config = get_database_config()

    with psycopg.connect(
        host=config["host"],
        port=config["port"],
        dbname=config["dbname"],
        user=config["user"],
        password=config["password"],
        ) as connection, connection.cursor() as cursor:
        cursor.execute("SELECT current_database(), current_user")
        row = cursor.fetchone()

        if row is None:
            raise RuntimeError("Database connection check returned no row")

        database, user = row

    print(f"Database connection successful: database={database}, user={user}")


if __name__ == "__main__":
    main()
