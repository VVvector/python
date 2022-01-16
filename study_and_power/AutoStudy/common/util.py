# -*- coding:utf-8 -*-
import logging
import os

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


def get_logger(logger_name):
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter(
        '[%(asctime)s][%(thread)d][%(filename)s][line: %(lineno)d][%(levelname)s] %(message)s')

    # console log设置
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    # file log设置
    cur_path = os.path.dirname(os.path.abspath(__file__))
    cur_path = os.path.join(cur_path, "test.log")
    fh = logging.FileHandler(cur_path)
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(formatter)
    logger.addHandler(fh)

    return logger
