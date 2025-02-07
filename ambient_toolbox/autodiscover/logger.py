import logging

from ambient_toolbox.autodiscover.settings import get_autodiscover_logger_name


def get_logger() -> logging.Logger:
    """
    Returns an instance of a toolbox Django logger
    """
    return logging.getLogger(get_autodiscover_logger_name())
