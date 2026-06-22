import logging
import sys

def setup_logger():

    logger = logging.getLogger("inventory_service")
    logger.setLevel(logging.INFO)

    # Prevent duplicating logs if setup_logger is called twice
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            "%(asctime)s - [INVENTORY] - %(levelname)s - %(message)s"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger

logger = setup_logger()