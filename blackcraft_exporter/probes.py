import asyncio
from typing import Awaitable

import mcstatus
from mcstatus.status_response import BaseStatusResponse
from typing_extensions import Callable

from blackcraft_exporter.context import ProbeContext
from blackcraft_exporter.logger import get_logger
from blackcraft_exporter.mc import JavaServerPlus

ProbeFunc = Callable[[ProbeContext], Awaitable[None]]
MAX_INFO_FIELD_LENGTH = 256


def __handle_server_status(ctx: ProbeContext, status: BaseStatusResponse):
	ctx.gauge(name='probe_latency_seconds', doc='Time taken for status probe in seconds, aka. server ping').set(status.latency / 1000)
	ctx.gauge(name='server_players_online', doc='Current number of players online').set(status.players.online)
	ctx.gauge(name='server_players_max', doc='Maximum number of players allowed on the server').set(status.players.max)
	ctx.gauge(name='server_info', doc='Detailed information about the server', labels={
		'version': status.version.name[:MAX_INFO_FIELD_LENGTH],
		'protocol': str(status.version.protocol),
		'motd': status.motd.to_plain()[:MAX_INFO_FIELD_LENGTH],
	}).set(1)


async def probe_java(ctx: ProbeContext):
	async def do_probe() -> BaseStatusResponse:
		with ctx.time_cost_gauge('probe_srv_lookup_seconds', 'Time taken for SRV record lookup in seconds'):
			server = await JavaServerPlus.async_lookup(ctx.target)
		get_logger().debug(f'JavaServer lookup result for {ctx.target!r}: {server.address}')

		return await server.async_status()

	status = await asyncio.wait_for(do_probe(), timeout=ctx.get_timeout_remaining())
	__handle_server_status(ctx, status)


async def probe_bedrock(ctx: ProbeContext):
	async def do_probe() -> BaseStatusResponse:
		server = mcstatus.BedrockServer(ctx.target)
		return await server.async_status()

	status = await asyncio.wait_for(do_probe(), timeout=ctx.get_timeout_remaining())
	__handle_server_status(ctx, status)
