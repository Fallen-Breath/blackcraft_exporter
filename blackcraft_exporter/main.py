import logging

import uvicorn

from blackcraft_exporter.config import load_config_from_argv
from blackcraft_exporter.logger import get_logger  # this also triggers our logging boostrap


def main():
	config = load_config_from_argv()

	logger = get_logger()
	if config.debug:
		logger.setLevel(logging.DEBUG)
	logger.debug(f'Debug mode on')
	logger.debug(f'{config!r}')

	uvicorn.run(
		app='blackcraft_exporter.server:app',
		host=config.host,
		port=config.port,
		workers=config.workers,
		reload=config.dev_mode,
	)
