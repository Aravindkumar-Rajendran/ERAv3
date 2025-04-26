import logging
import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
def setup_logging():
    # Create logs directory if it doesn't exist
    log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
    os.makedirs(log_dir, exist_ok=True)
    
    # Set up the root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    
    # Create formatters
    console_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)
    
    # File handler
    log_file = os.path.join(log_dir, 'app.log')
    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(file_formatter)
    root_logger.addHandler(file_handler)
    
    # Set log levels from environment variables
    log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
    root_logger.setLevel(getattr(logging, log_level))
    
    # Configure specific loggers
    loggers = {
        'app': logging.INFO,
        'uvicorn': logging.INFO,
        'fastapi': logging.INFO,
        'sqlalchemy': logging.WARNING
    }
    
    for logger_name, level in loggers.items():
        logger = logging.getLogger(logger_name)
        logger.setLevel(level)
        logger.addHandler(console_handler)
        logger.addHandler(file_handler)
        logger.propagate = False

# Call setup_logging when this module is imported
setup_logging()

# Create and export a logger instance
logger = logging.getLogger('app') 