import os
from logging.config import dictConfig

import structlog


LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        # JSON formatter for file logs (no colors, structured).
        "json": {
            "()": "structlog.stdlib.ProcessorFormatter",
            "processor": structlog.processors.JSONRenderer(),
            "foreign_pre_chain": [
                structlog.processors.TimeStamper(fmt="iso"),
                structlog.processors.add_log_level,
            ],
        },
        # Structlog-aware formatter for console with colors.
        "structlog_console": {
            "()": "structlog.stdlib.ProcessorFormatter",
            "processor": structlog.dev.ConsoleRenderer(),  # colored output
            "foreign_pre_chain": [
                structlog.processors.TimeStamper(fmt="iso"),
                structlog.processors.add_log_level,
            ],
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "structlog_console",
        },
        # "file" handler is injected at runtime in setup_logging so we can
        # ensure the logs directory exists and configure rotation.
    },
    "root": {
        "level": "INFO",
        "handlers": ["console"],
    },
}


def setup_logging() -> None:
    """
    Configure application-wide logging using structlog on top of the standard
    library logging stack, with daily rotating log files.
    """
    # Ensure base logs directory exists.
    log_dir = os.path.join("logs")
    os.makedirs(log_dir, exist_ok=True)

    LOGGING_CONFIG["handlers"]["file"] = {
        "class": "logging.handlers.TimedRotatingFileHandler",
        "formatter": "json",
        "filename": os.path.join(log_dir, "app.log"),
        "when": "midnight",
        "interval": 1,
        "backupCount": 7,  # keep one week of history
        "encoding": "utf-8",
        "utc": False,
    }
    LOGGING_CONFIG["root"]["handlers"] = ["console", "file"]

    dictConfig(LOGGING_CONFIG)

    structlog.configure(
        processors=[
            structlog.stdlib.add_log_level,
            structlog.stdlib.add_logger_name,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            # Hand off to logging's ProcessorFormatter, which will:
            # - Use ConsoleRenderer (colors) for console
            # - Use plain formatter for file
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )


def get_logger(name: str):
    """
    Convenience helper to get a module-specific structured logger.
    """
    return structlog.get_logger(name)
