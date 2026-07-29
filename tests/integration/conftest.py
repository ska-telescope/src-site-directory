import logging
import os
import sys

logging.basicConfig(level=logging.INFO, stream=sys.stdout, force=True)

SCAPI_URL = os.getenv("SCAPI_URL", "http://scapi-core:8080")
SCAPI_SERVICE_VERSION = os.getenv("SCAPI_SERVICE_VERSION", "v1")
SCAPI_SERVICE_URL = f"{SCAPI_URL}/{SCAPI_SERVICE_VERSION}"

try:
    from ska_src_logging import get_logger as _get_logger

    logger = _get_logger("scapi_tests", name=__name__)
except ImportError:
    logger = logging.getLogger(__name__)
