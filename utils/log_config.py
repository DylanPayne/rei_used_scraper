import logging

def log_config(log_file):
    logger = logging.getLogger(__name__)
    logger.propogate = False # to prevent sqlalchemy logging from being set to INFO

    # Create a handler to write logs to a file
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.INFO)

    # Define the log format
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    file_handler.setFormatter(formatter)

    # Add the file handler to the logger
    logger.addHandler(file_handler)

    return logger
