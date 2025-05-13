from typing import Optional

from pydantic import BaseModel, ConfigDict, field_validator, Field

from blackcraft_exporter import utils
from blackcraft_exporter.probes import SERVER_TYPES


# noinspection PyNestedDecorators
class ProbeRequest(BaseModel):
	model_config = ConfigDict(extra='forbid')

	type: str
	target: str
	timeout: float = Field(default=10, ge=0)
	mimic: Optional[str] = None
	proxy: Optional[str] = None
	max_attempts: int = Field(default=1, ge=1)

	@field_validator('type')
	@classmethod
	def validate_type(cls, server_type: str) -> str:
		if server_type not in SERVER_TYPES:
			raise ValueError(f"Invalid type: {server_type!r}, should be one of {', '.join(SERVER_TYPES.keys())}")
		return server_type

	@field_validator('target')
	@classmethod
	def validate_target(cls, target: str) -> str:
		if not utils.validate_ip_port(target, needs_port=False):
			raise ValueError(f"Invalid target: {target!r}")
		return target

	@field_validator('mimic')
	@classmethod
	def validate_mimic(cls, mimic: Optional[str]) -> Optional[str]:
		if not utils.validate_ip_port(mimic, needs_port=True):
			raise ValueError(f"Invalid mimic: {mimic!r}")
		return mimic

	@field_validator('proxy')
	@classmethod
	def validate_proxy(cls, proxy: Optional[str]) -> Optional[str]:
		from python_socks import parse_proxy_url
		if proxy:
			parse_proxy_url(proxy)
		return proxy
