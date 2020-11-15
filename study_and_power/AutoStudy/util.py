# -*- coding:utf-8 -*-
import logging


DEFAULT_LOGGING_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
logging_file = "./temp/log.txt"
_logger = None


def init_logger(name=__name__):
    global _logger
    logging._acquireLock()
    try:
        if not _logger:
            _logger = logging.getLogger(name)
            _logger.setLevel(level=logging.INFO)
            formatter = logging.Formatter(DEFAULT_LOGGING_FORMAT)

            handler = logging.FileHandler(logging_file)
            handler.setLevel(logging.INFO)
            handler.setFormatter(formatter)

            console = logging.StreamHandler()
            console.setLevel(logging.INFO)
            console.setFormatter(formatter)

            _logger.addHandler(handler)
            _logger.addHandler(console)
    finally:
        logging._releaseLock()

    return _logger