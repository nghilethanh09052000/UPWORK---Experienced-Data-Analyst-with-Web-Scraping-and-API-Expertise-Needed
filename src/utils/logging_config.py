import logging
import sys
import os

# Add src to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

from config.settings import LOG_LEVEL, LOG_FORMAT, LOG_FILE

def setup_logging():
    """Configure logging for the application"""
    # Create formatter
    formatter = logging.Formatter(LOG_FORMAT)
    
    # Create handlers
    file_handler = logging.FileHandler(LOG_FILE)
    file_handler.setFormatter(formatter)
    
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    
    # Get root logger
    logger = logging.getLogger()
    logger.setLevel(LOG_LEVEL)
    
    # Remove existing handlers
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Add handlers
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger 