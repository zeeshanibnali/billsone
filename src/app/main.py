"""ASGI entry: logging, app instance, and dev server when run as a script."""

import uvicorn

from app.core.env import get_uvicorn_settings
from app.core.logger import get_logger, setup_logging
from app.factory import create_app

setup_logging()
logger = get_logger(__name__)

app = create_app()


def main() -> None:
    settings = get_uvicorn_settings()
    logger.info(
        "Running development server with uvicorn",
        host=settings.host,
        port=settings.port,
        reload=settings.reload,
    )
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.reload,
    )


if __name__ == "__main__":
    main()
