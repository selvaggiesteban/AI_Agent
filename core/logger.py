import logging
import os
from datetime import datetime

def setup_logger(name="AI_Agent"):
    """
    Configures a logger that writes to both a file in the logs directory and the console.
    """
    log_dir = os.path.join(os.getcwd(), "logs")
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # Create filename based on current date
    today = datetime.now().strftime("%Y-%m-%d")
    log_file = os.path.join(log_dir, f"agent_{today}.log")

    # Configure logger
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    # Prevent duplicate handlers if setup_logger is called multiple times
    if not logger.handlers:
        # File Handler
        fh = logging.FileHandler(log_file, encoding="utf-8")
        fh.setLevel(logging.INFO)

        # Console Handler
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)

        # Formatter
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)

        logger.addHandler(fh)
        logger.addHandler(ch)

    return logger

# Global logger instance
logger = setup_logger()
