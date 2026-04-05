import os

from app.core.logger import get_logger
from app.database.engine import SessionLocal
from app.database.seeder import seed_db


logger = get_logger(__name__)


def _seed_dummy_data_enabled() -> bool:
    raw = os.getenv("SEED_DUMMY_DATA", "")
    return str(raw).strip().lower() in ("1", "true", "yes")


def init_db() -> None:
    """
    Optionally seed demo rows when the database is empty.

    Seeding runs only if ``SEED_DUMMY_DATA`` is truthy (see README).

    Apply schema changes with Alembic: ``uv run alembic upgrade head``
    (before deploy or on first setup).
    """
    logger.info("Initializing database...")

    if not _seed_dummy_data_enabled():
        logger.info("SEED_DUMMY_DATA not enabled; skipping demo seed")
        return

    db = SessionLocal()
    try:
        seed_db(db)
        logger.info("Dummy data seeded (if database was empty)")
    finally:
        db.close()
