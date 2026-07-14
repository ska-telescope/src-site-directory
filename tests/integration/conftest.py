import logging
import sys

logging.basicConfig(level=logging.INFO, stream=sys.stdout, force=True)

try:
    from ska_src_logging import get_logger as _get_logger

    logger = _get_logger("scapi_tests", name=__name__)
except ImportError:
    logger = logging.getLogger(__name__)
