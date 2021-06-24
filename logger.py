import os
import logging
import sys


class CONFIG:

    stdout_level = logging.WARNING
    file_level = logging.WARNING
    path = 'logs/'
    tofile = False
    datefmt = '%Y-%m-%d %H:%M:%S'
    fmt = '%(asctime)s|%(name)s|%(levelname)s|%(message)s'


def get_logger(
        name,
        stdout_level=CONFIG.stdout_level,
        file_level=CONFIG.file_level,
        path=CONFIG.path,
        tofile=CONFIG.tofile,
        datefmt=CONFIG.datefmt,
        fmt=CONFIG.fmt
    ):

    # create logger and set level
    logger = logging.getLogger(name=name)
    logger.setLevel(level=logging.DEBUG)

    # create formatter
    formatter = logging.Formatter(fmt=fmt, datefmt=datefmt)

    # add stream handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.setLevel(level=stdout_level)
    logger.addHandler(console_handler)

    # if write to file
    if tofile:
        if not os.path.exists(path):
            os.mkdir(path)

        if not os.path.exists(path+name):
            open(path+name, 'w').close()

        # add file handler
        file_handler = logging.FileHandler(path+name)
        file_handler.setFormatter(formatter)
        file_handler.setLevel(level=file_level)
        logger.addHandler(file_handler)

    return logger


if __name__ == '__main__':

    DEBUG = True

    # create logger
    if DEBUG:
        logger = get_logger(__name__, stdout_level=logging.INFO)
    else:
        logger = get_logger(__name__, stdout_level=logging.WARNING, file_level=logging.INFO, tofile=True)

    logger.warning('warning')
    logger.info('info')
    logger.debug('debug')
