import uvicorn
from uvicorn.config import LOGGING_CONFIG

from blackcraft_exporter.config import load_config_from_argv


def boostrap():
	for cfg in LOGGING_CONFIG['formatters'].values():
		cfg['fmt'] = '%(process)s %(asctime)s.%(msecs)03d - ' + cfg['fmt']
		cfg['datefmt'] = '%Y-%m-%d %H:%M:%S'


def main():
	boostrap()
	config = load_config_from_argv()

	uvicorn.run(
		app='blackcraft_exporter.server:app',
		host=config.host,
		port=config.port,
		workers=config.workers,
		reload=config.dev_mode,
	)
