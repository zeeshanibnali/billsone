"""Project paths and environment loading (single place for `.env`)."""

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

# example/ — stable regardless of cwd (e.g. uvicorn, scripts)
PROJECT_ROOT = Path(__file__).resolve().parents[3]
ENV_FILE = PROJECT_ROOT / ".env"
load_dotenv(ENV_FILE)


def _env_bool(key: str, default: bool) -> bool:
    raw = os.getenv(key)
    if raw is None or not str(raw).strip():
        return default
    return str(raw).strip().lower() in ("1", "true", "yes", "on")


@dataclass(frozen=True)
class UvicornSettings:
    host: str
    port: int
    reload: bool


def get_uvicorn_settings() -> UvicornSettings:
    host = (os.getenv("UVICORN_HOST") or "0.0.0.0").strip() or "0.0.0.0"
    port_raw = (os.getenv("UVICORN_PORT") or "8000").strip()
    try:
        port = int(port_raw)
    except ValueError as exc:
        msg = f"Invalid UVICORN_PORT: {port_raw!r}. Expected an integer."
        raise SystemExit(msg) from exc
    if not (1 <= port <= 65535):
        raise SystemExit(f"Invalid UVICORN_PORT: {port}. Expected 1–65535.")
    reload = _env_bool("UVICORN_RELOAD", True)
    return UvicornSettings(host=host, port=port, reload=reload)
