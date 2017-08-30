# -*- coding: utf-8 -*-
# configure logging such that:
# - DEBUG and above are logged to stdout as JSON
# - noisy dependant modules are logged at WARN
import logging
import logging.config

default_logging_config = {
    'version': 1,
    'formatters': {
        'json': {
            'format': '{'
            '"level": "%(levelname)s", '
            '"msg": "%(message)s", '
            '"source": "%(filename)s:%(lineno)d", '
            '"pid": "%(process)d", '
            '"time": "%(asctime)s" ,'
            '"name": "%(name)s"'
            '}',
        },
    },
    'handlers': {
        'stdout': {
            'class': 'logging.StreamHandler',
            'formatter': 'json',
            'level': logging.DEBUG,
            'stream': 'ext://sys.stdout',
        },
    },
    'loggers': {
        '': {
            'handlers': [
                'stdout',
            ],
            'level': logging.INFO,
            'propagate': False,
        },
        'securityserverpy': {
            'handlers': [
                'stdout',
            ],
            'level': logging.DEBUG,
            'propagate': False,
        }
    }
}

logging.config.dictConfig(default_logging_config)
_logger = logging.getLogger(__name__)