from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

from config import DATABASE_URL

# ── Engine ───────────────────────────────────────────────────────────────────
# connect_timeout / read_timeout / write_timeout are critical: without them,
# a slow or unreachable MySQL host (common on Render, where the DB may be on
# a different network / provider) makes every query hang indefinitely with
# no error, which looks like the whole chatbot is "stuck".
_engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=280,  # avoid "MySQL server has gone away" on idle Render dynos
    connect_args={
        "connect_timeout": 5,   # seconds to establish the TCP/MySQL handshake
        "read_timeout": 8,      # seconds to wait for a query result
        "write_timeout": 8,
    },
)


def execute_query(sql: str, params: dict | None = None) -> list[dict]:
    """
    Run a parameterized statement and return rows as dicts.
    Uses SQLAlchemy :name bound parameters (works with PyMySQL).

    Raises a clear RuntimeError (instead of hanging) if the DB is
    unreachable or the query fails, so callers/tools can surface a
    real error to the user instead of leaving the request stuck.
    """
    params = params or {}
    try:
        with _engine.connect() as conn:
            result = conn.execute(text(sql), params)
            return [dict(row._mapping) for row in result]
    except SQLAlchemyError as exc:
        raise RuntimeError(f"Database connection/query failed: {exc}") from exc
