import logging

from ambient_toolbox.autodiscover.logger import get_logger
from ambient_toolbox.autodiscover.settings import get_autodiscover_logger_name


def test_get_logger():
    logger = get_logger()

    assert isinstance(logger, logging.Logger)
    assert logger.name == get_autodiscover_logger_name()
