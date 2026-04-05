"""UTC helpers for persisted timestamps."""

from datetime import datetime, timezone


def utc_now() -> datetime:
    """Current instant in UTC (timezone-aware), for DateTime(timezone=True) columns."""
    return datetime.now(timezone.utc)
