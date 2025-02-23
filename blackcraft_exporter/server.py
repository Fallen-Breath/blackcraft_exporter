from typing import Annotated

import dns
from fastapi import FastAPI, Query
from fastapi.middleware.gzip import GZipMiddleware
from prometheus_client import generate_latest, CollectorRegistry
from starlette.responses import PlainTextResponse

from blackcraft_exporter import __version__
from blackcraft_exporter.config import get_config
from blackcraft_exporter.context import ProbeContext
from blackcraft_exporter.dto import ProbeRequest
from blackcraft_exporter.logger import get_logger
from blackcraft_exporter.probes import SERVER_TYPES

app = FastAPI()
app.add_middleware(GZipMiddleware)
logger = get_logger()


@app.get('/', response_class=PlainTextResponse)
async def root():
	return 'BlackCraft Exporter is running'


@app.get('/probe', response_class=PlainTextResponse)
async def probe(req: Annotated[ProbeRequest, Query()]):
	probe_func = SERVER_TYPES[req.type]

	ctx = ProbeContext(
		registry=CollectorRegistry(auto_describe=True),
		target=req.target,
		timeout=req.timeout,
		mimic=req.mimic,
		proxy=req.proxy,
		max_attempts=req.max_attempts,
	)
	with ctx.time_cost_gauge(name='probe_duration_seconds', doc='Time taken for status probe in seconds'):
		probe_success = 0
		try:
			await probe_func(ctx)
		except (TimeoutError, dns.exception.Timeout):
			logger.error(f'Probe timed out, req {req!r}')
		except Exception as e:
			msg = f'Probe failed, req {req!r}: ({type(e)}) {e}'
			(logger.exception if get_config().dev_mode else logger.error)(msg)
		else:
			probe_success = 1
		ctx.gauge(name='probe_success', doc='Displays whether or not the probe was a success').set(probe_success)

	return generate_latest(ctx.registry)


@app.get('/metrics', response_class=PlainTextResponse)
async def metrics():
	return generate_latest()


def __init():
	logger.info(f'Starting BlackCraft Exporter v{__version__}')
	if get_config().dev_mode:
		logger.warning('Development mode on')


__init()
