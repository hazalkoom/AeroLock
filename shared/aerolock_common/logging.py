import logging
import sys

def setup_logger(name: str) -> logging.Logger:
    """Configures a standardized console logger for AeroLock services."""
    logger = logging.getLogger(name)
    
    # Only configure if it hasn't been configured yet to avoid duplicate logs
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
    return logger

