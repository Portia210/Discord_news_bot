import logging
from logging.handlers import RotatingFileHandler

def setup_logger(name="logger", level=logging.DEBUG, log_file=None):
    """
    Sets up a logger with both console and file handlers.
    
    Args:
        name (str): Name of the logger
        level (int): Logging level (default: DEBUG)
        log_file (str, optional): Log file name
    
    Returns:
        logging.Logger: Configured logger
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    if not logger.hasHandlers():
        # Formatter with filename and line number
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )

        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(level)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        # File handler (if log_file is provided)
        if log_file:
            file_handler = RotatingFileHandler(log_file, maxBytes=5000000, encoding='utf-8')
            file_handler.setLevel(level)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)

    return logger

# Create default logger instance
logger = setup_logger(name="logger", level=logging.DEBUG, log_file="logger.log")