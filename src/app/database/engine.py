from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database.config import DATABASE_URL

# Evaluate CURRENT_TIMESTAMP / now() in UTC so server-side defaults match app-side UTC.
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    connect_args={"options": "-c timezone=UTC"},
)

SessionLocal = sessionmaker(bind=engine)
