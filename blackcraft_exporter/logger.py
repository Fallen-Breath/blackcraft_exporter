import copy
import logging
from logging.config import dictConfig

from uvicorn.config import LOGGING_CONFIG as UVICORN_LOGGING_CONFIG

from blackcraft_exporter.constants import MODULE_NAME


def __boostrap():
	for cfg in UVICORN_LOGGING_CONFIG['formatters'].values():
		cfg['fmt'] = '%(process)s %(asctime)s.%(msecs)03d - ' + cfg['fmt']
		cfg['datefmt'] = '%Y-%m-%d %H:%M:%S'

	logging_config = copy.deepcopy(UVICORN_LOGGING_CONFIG)
	logging_config['loggers'][MODULE_NAME] = {
		'handlers': ['default'],
		'level': 'INFO',
		'propagate': False,
	}
	dictConfig(logging_config)

	global __logger
	__logger = logging.getLogger(MODULE_NAME)


def get_logger() -> logging.Logger:
	return __logger


__logger: logging.Logger
__boostrap()
