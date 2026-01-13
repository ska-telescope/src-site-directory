"""Logging configuration for Site Capabilities API using ska-src-logging integrations."""

from ska_src_logging import get_logger
from ska_src_logging.integrations.fastapi import LoggingContextMiddleware, setup_uvicorn_logging

# Get the ska-src-logging logger
logger = get_logger("SCAPI")

# Export for convenience
__all__ = ["logger", "LoggingContextMiddleware", "setup_uvicorn_logging"]


def setup_logging():
    """Setup logging for Site Capabilities API."""
    setup_uvicorn_logging("SCAPI")
