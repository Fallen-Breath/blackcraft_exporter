from typing import Annotated

import dns
from fastapi import FastAPI, Query
from fastapi.middleware.gzip import GZipMiddleware
from prometheus_client import generate_latest, CollectorRegistry
from pydantic import BaseModel, ConfigDict, field_validator, Field
from starlette.responses import PlainTextResponse

from blackcraft_exporter import __version__, utils
from blackcraft_exporter.config import get_config
from blackcraft_exporter.context import ProbeContext
from blackcraft_exporter.logger import get_logger
from blackcraft_exporter.probes import probe_java, probe_bedrock, ProbeFunc

app = FastAPI()
app.add_middleware(GZipMiddleware)
logger = get_logger()


@app.get('/', response_class=PlainTextResponse)
async def root():
	return 'BlackCraft Exporter is running'


SERVER_TYPES: dict[str, ProbeFunc] = {
	'java': probe_java,
	'bedrock': probe_bedrock,
}


# noinspection PyNestedDecorators
class ProbeRequest(BaseModel):
	model_config = ConfigDict(extra='forbid')

	type: str
	target: str
	timeout: float = Field(default=10, ge=0)

	@field_validator('type')
	@classmethod
	def validate_type(cls, v: str) -> str:
		if v not in SERVER_TYPES:
			raise ValueError(f"Invalid type: {v!r}, should be one of {', '.join(SERVER_TYPES.keys())}")
		return v

	@field_validator('target')
	@classmethod
	def validate_target(cls, v: str) -> str:
		if not utils.validate_ip_port(v):
			raise ValueError(f"Invalid target: {v!r}")
		return v


@app.get('/probe', response_class=PlainTextResponse)
async def probe(req: Annotated[ProbeRequest, Query()]):
	probe_func = SERVER_TYPES[req.type]

	ctx = ProbeContext(CollectorRegistry(auto_describe=True), req.target, req.timeout)
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
