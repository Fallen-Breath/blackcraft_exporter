import uvicorn
from uvicorn.config import LOGGING_CONFIG

from blackcraft_exporter.config import load_config_from_argv


def main():
	LOGGING_CONFIG['formatters']['default']['fmt'] = '%(process)s %(asctime)s.%(msecs)03d %(levelprefix)s %(message)s'
	config = load_config_from_argv()
	uvicorn.run(
		app='blackcraft_exporter.server:app',
		host=config.host,
		port=config.port,
		workers=config.workers,
		reload=config.dev_mode,
	)
