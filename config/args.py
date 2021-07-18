import logging


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

datafmt = '%Y-%m-%d %H:%M:%S'
