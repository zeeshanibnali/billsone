"""Application factory: wire FastAPI, middleware, routers, and handlers."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from app.core.exception_handlers import register_exception_handlers
from app.core.logger import get_logger
from app.core.rate_limit import limiter
from app.database.init import init_db
from app.modules.bills.bills_controller import router as bill_router

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting application, initializing database...")
    init_db()
    yield


def create_app() -> FastAPI:
    app = FastAPI(
        title="Billing API - BillsOne",
        description="API for managing bills and sub-bills.",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )

    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
    app.add_middleware(SlowAPIMiddleware)
    register_exception_handlers(app)

    @app.get("/")
    def read_root():
        return {"Hello": "Welcome to the BillsOne API"}

    app.include_router(bill_router)
    return app
