from fastapi import FastAPI
import uvicorn

from app.database.init import init_db  # 👈 import this
from app.modules.bills.bills_controller import router as bill_router

app = FastAPI()


@app.on_event("startup")
def startup():
    init_db()  # 👈 runs every time server starts


@app.get("/")
def read_root():
    return {"Hello": "World"}


app.include_router(bill_router)


def main():
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)


if __name__ == "__main__":
    main()
