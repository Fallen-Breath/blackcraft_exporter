import uvicorn

from blackcraft_exporter.config import load_config_from_argv


def main():
	config = load_config_from_argv()
	uvicorn.run(
		app='blackcraft_exporter.server:app',
		host=config.host,
		port=config.port,
		workers=config.workers,
	)
