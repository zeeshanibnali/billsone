from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.modules.bills.bills_entity import BillEntity

# In-memory SQLite
DATABASE_URL = "sqlite+pysqlite:///:memory:"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,  # 🔥 keeps DB alive
)

SessionLocal = sessionmaker(bind=engine)


def get_all_bills():
    db = SessionLocal()
    try:
        bills = db.query(BillEntity).all()
        return bills
    finally:
        db.close()
