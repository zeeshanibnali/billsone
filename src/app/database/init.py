from app.database.base import Base
from app.database.engine import engine, SessionLocal
from app.modules.bills.bills_entity import BillEntity


def init_db():
    print("\n🚀 Initializing DB...")

    # Step 2: create table
    Base.metadata.create_all(bind=engine)
    print("✅ Table created")

    db = SessionLocal()

    # Step 3: insert bill
    new_bill = BillEntity(total=500)
    db.add(new_bill)
    db.commit()
    print("✅ Inserted bill")

    # Step 4: query all bills
    bills = db.query(BillEntity).all()

    print("📄 Bills in DB:")
    for b in bills:
        print(f"id={b.id}, total={b.total}")

    db.close()
