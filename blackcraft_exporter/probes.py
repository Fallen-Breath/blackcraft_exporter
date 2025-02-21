import asyncio
from typing import Awaitable

import mcstatus
from mcstatus.status_response import BaseStatusResponse
from typing_extensions import Callable

from blackcraft_exporter.context import ProbeContext

ProbeFunc = Callable[[ProbeContext], Awaitable[None]]
MAX_INFO_FIELD_LENGTH = 256


async def __handle_server_status(ctx: ProbeContext, status: BaseStatusResponse):
	ctx.gauge(name='probe_latency_seconds', doc='Time taken for status probe in seconds').set(status.latency / 1000)
	ctx.gauge(name='server_players_online', doc='Current number of players online').set(status.players.online)
	ctx.gauge(name='server_players_max', doc='Maximum number of players allowed on the server').set(status.players.max)
	ctx.gauge(name='server_info', doc='Detailed information about the server', labels={
		'version': status.version.name[:MAX_INFO_FIELD_LENGTH],
		'protocol': status.version.protocol,
		'motd': status.motd.to_plain()[:MAX_INFO_FIELD_LENGTH],
	}).set(1)


async def probe_java(ctx: ProbeContext):
	async def do_probe() -> BaseStatusResponse:
		with ctx.time_cost_gauge('probe_srv_lookup_seconds', 'The time taken for SRV record lookup in seconds'):
			server = await mcstatus.JavaServer.async_lookup(ctx.target, timeout=ctx.timeout)
		return await server.async_status()

	status = await asyncio.wait_for(do_probe(), timeout=ctx.timeout)
	await __handle_server_status(ctx, status)


async def probe_bedrock(ctx: ProbeContext):
	server = mcstatus.BedrockServer(ctx.target)
	status = await asyncio.wait_for(server.async_status(), timeout=ctx.timeout)
	await __handle_server_status(ctx, status)
