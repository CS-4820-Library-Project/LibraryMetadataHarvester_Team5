import logging

# Set up logging configuration
logging.basicConfig(filename='lmh_log.log',
                    filemode='a',  # Append to the log file
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    level=logging.INFO)


def log_info(message):
    logging.info(message)


def log_warning(message):
    logging.warning(message)


def log_error(message):
    logging.error(message)
