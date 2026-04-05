"""Build the PostgreSQL SQLAlchemy URL with validation (`.env` via `app.core.env`)."""

import os
from urllib.parse import quote_plus

from app.core.env import ENV_FILE


def _missing_or_blank_env(keys: tuple[str, ...]) -> list[str]:
    """Return keys that are unset or empty/whitespace."""
    missing: list[str] = []
    for key in keys:
        raw = os.getenv(key)
        if raw is None or not str(raw).strip():
            missing.append(key)
    return missing


def _parse_port(port_raw: str, *, key: str = "DATABASE_PORT") -> int:
    try:
        port = int(str(port_raw).strip())
    except (TypeError, ValueError) as exc:
        msg = f"Invalid {key}: {port_raw!r}. Expected an integer between 1 and 65535."
        raise RuntimeError(msg) from exc
    if not (1 <= port <= 65535):
        msg = f"Invalid {key}: {port_raw!r}. Expected an integer between 1 and 65535."
        raise RuntimeError(msg)
    return port


def build_database_url() -> str:
    """Build a PostgreSQL connection URL (psycopg v3 driver)."""
    required = (
        "DATABASE_HOST",
        "DATABASE_PORT",
        "DATABASE_USERNAME",
        "DATABASE_PASSWORD",
        "DATABASE_NAME",
    )
    missing = _missing_or_blank_env(required)
    if missing:
        joined = ", ".join(missing)
        msg = (
            f"Missing required environment variable(s): {joined}. "
            f"Set them in {ENV_FILE} or export them in your shell."
        )
        raise RuntimeError(msg)

    user = os.environ["DATABASE_USERNAME"].strip()
    password = os.environ["DATABASE_PASSWORD"]
    host = os.environ["DATABASE_HOST"].strip()
    port = str(_parse_port(os.environ["DATABASE_PORT"]))
    name = os.environ["DATABASE_NAME"].strip()

    safe_user = quote_plus(user)
    safe_password = quote_plus(password)
    return f"postgresql+psycopg://{safe_user}:{safe_password}@{host}:{port}/{name}"


DATABASE_URL = build_database_url()
