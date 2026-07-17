import logging
import sys

import structlog


def _configure_structlog() -> None:
    """Set up structlog with a standard-library handler so logs are visible.

    Without this, ``structlog.stdlib.LoggerFactory()`` sends events into
    Python's ``logging`` machinery — but if no handler is installed the
    messages are silently dropped.
    """
    # Ensure there is at least one handler on the root logger
    # so structlog events are not swallowed.
    root = logging.getLogger()
    if not root.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(logging.Formatter("%(message)s"))
        root.addHandler(handler)
        root.setLevel(logging.INFO)

    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.stdlib.add_log_level,
            structlog.stdlib.add_logger_name,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.dev.ConsoleRenderer(colors=True),
        ],
        wrapper_class=structlog.stdlib.BoundLogger,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )


def get_logger(name: str | None = None) -> structlog.stdlib.BoundLogger:
    """Return a structured logger, configuring once on first call."""
    if not structlog.is_configured():
        _configure_structlog()
    return structlog.get_logger(name)
