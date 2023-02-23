"""Logging module. This can be extended with more features like
logging to file as well as console, etc.,
"""
import logging
import sys
import traceback

NAME = "WEBSITE_GENERATOR"


def setup_logging(log_level="DEBUG"):
    """Configure the logger object

    Args:
      log_level (str): The minimum log level severity that should be considered
                       for logging.
                       Defaults to 'DEBUG'
    """

    log_level = getattr(logging, log_level)
    # Custom variables
    logging.marker = "-" * 60
    logging.step = 1
    logging.stage = ''

    # Create the loggers
    logging.website_generator_logger = logging.getLogger(NAME)

    # Remove all existing handlers
    logging.website_generator_logger.handlers = []

    # Disable the root logger
    logging.getLogger().disabled = True

    # Construct the formatter
    formatter = __get_formatter()

    # setup console handler
    console_handler = logging.StreamHandler(stream=sys.stdout)
    console_handler.setFormatter(formatter)
    logging.website_generator_logger.addHandler(console_handler)

    # configure logger
    logging.website_generator_logger.setLevel(log_level)
    logging.website_generator_logger.propagate = 0


def __get_formatter():
    formatter = logging.Formatter('%(asctime)s (%(threadName)s) %(levelname)s '
                                  '[%(file_line)s] : %(message)s')
    return formatter


def set_level(level):
    """Sets the logging level to the desired one.

    Args:
      level (int): The desired log level

    Returns:
      None
    """
    logging.website_generator_logger.setLevel(level)


def INFO(msg):
    logging.website_generator_logger.info(msg, extra=__extra())


def WARN(msg):
    logging.website_generator_logger.warn(msg, extra=__extra())


def ERROR(msg):
    logging.website_generator_logger.error(msg, extra=__extra())


def CRITICAL(msg):
    logging.website_generator_logger.critical(msg, extra=__extra())


def DEBUG(msg):
    logging.website_generator_logger.debug(msg, extra=__extra())


def LOGEXCEPTION(msg):
    logging.website_generator_logger.exception(msg, extra=__extra())


def log(level, msg, *args, **kwargs):
    logging.website_generator_logger.log(
        level, msg, extra=__extra(), *args, **kwargs)


def __extra():
    frame = traceback.extract_stack()[-3]
    file_name = frame[0].split("/")[-1]
    file_line = frame[1]
    return {
        'file_line': "%s:%s" % (file_name, file_line)
    }


setup_logging()
