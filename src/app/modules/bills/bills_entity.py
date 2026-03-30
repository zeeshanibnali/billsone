from sqlalchemy import Column, Integer, Float
from app.database.base import Base


class BillEntity(Base):
    __tablename__ = "bills"

    id = Column(Integer, primary_key=True, index=True)
    total = Column(Float)
