import logging, os
from logging.handlers import RotatingFileHandler

testing = False

def setup_logging(log_file, logger_name):
    # Remove the existing log file if it exists
    if os.path.exists(log_file):
        os.remove(log_file)
    # Configure the root logger
    logger = logging.getLogger(logger_name)
    if testing:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)

    # Create a formatter
    formatter = logging.Formatter('%(name)-12s:%(asctime)s - %(levelname)s: %(message)s')

    # Create a rotating file handler
    file_handler = RotatingFileHandler(log_file, mode='w', maxBytes=1024 * 1024, backupCount=0)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    # Add the handler to the logger
    logger.addHandler(file_handler)

    return logger
