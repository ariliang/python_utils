import os, sys, logging
import logging.handlers


# default config
class _DEFAULT:

    stdout_level = logging.WARNING
    file_level = logging.WARNING
    datefmt = '%Y-%m-%d %H:%M:%S'
    fmt = '%(asctime)s|%(name)s|%(levelname)s|%(funcName)s@%(lineno)s|%(message)s'
    tofile = False
    path = 'logs/'              # default log file path
    timed_rotating = False      # change log file on scheduled
    when = 'D'                  # 'S', 'H', 'D', 'W0-W6'
    interval = 1


# get logger
def get_logger(
        name,
        stdout_level=_DEFAULT.stdout_level,
        file_level=_DEFAULT.file_level,
        datefmt=_DEFAULT.datefmt,
        fmt=_DEFAULT.fmt,
        tofile=_DEFAULT.tofile,
        path=_DEFAULT.path,
        timed_rotating=_DEFAULT.timed_rotating,
        when=_DEFAULT.when,
        interval=_DEFAULT.interval
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

        # add file handler
        file_name = os.path.join(path, name)

        if timed_rotating:
            file_handler = logging.handlers.TimedRotatingFileHandler(file_name, when=when, interval=interval)
        else:
            if not os.path.exists(file_name):
                open(file_name, 'w').close()

            file_handler = logging.FileHandler(file_name)

        file_handler.setFormatter(formatter)
        file_handler.setLevel(level=file_level)
        logger.addHandler(file_handler)

    return logger


# test
if __name__ == '__main__':

    DEBUG = True

    # create logger
    if DEBUG:
        log_config = {'stdout_level': logging.INFO}
    else:
        log_config = {
            'stdout_level': logging.WARNING,
            'file_level': logging.INFO,
            'tofile': True,
            'path': 'logs/',

            # scheduled
            # 'timed_rotating': True,
            # 'when': 'D',
            # 'interval': 30
        }

    logger = get_logger(__name__, **log_config)

    logger.warning('warning')
    logger.info('info')
    logger.debug('debug')
