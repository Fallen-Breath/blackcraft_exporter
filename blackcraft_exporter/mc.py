import asyncio
import socket
from typing import Optional

import mcstatus
from mcstatus import BedrockServer
from mcstatus.address import Address
from mcstatus.bedrock_status import BedrockServerStatus
from mcstatus.pinger import AsyncServerPinger
from mcstatus.protocol.connection import TCPAsyncSocketConnection
from mcstatus.status_response import JavaStatusResponse, BedrockStatusResponse
from typing_extensions import override

from blackcraft_exporter.context import ProbeContext
from blackcraft_exporter.logger import get_logger

logger = get_logger()


class TCPAsyncSocketConnectionPlus(TCPAsyncSocketConnection):
	"""
	1. Apply TCP_NODELAY to the socket
	2. Support proxy
	"""
	def __init__(self, address: Address, timeout: float, proxy: Optional[str] = None):
		super().__init__(address, timeout)
		self.proxy = proxy

	async def connect(self) -> None:
		if self.proxy:
			from python_socks.async_.asyncio import Proxy
			proxy = Proxy.from_url(self.proxy)
			sock = await proxy.connect(dest_host=self._addr.host, dest_port=self._addr.port)
			logger.info(f'Connected to proxy {proxy}')
			conn_coro = asyncio.open_connection(sock=sock)
		else:
			conn_coro = asyncio.open_connection(host=self._addr.host, port=self._addr.port)

		self.reader, self.writer = await asyncio.wait_for(conn_coro, timeout=self.timeout)
		sock = self.writer.transport.get_extra_info('socket')
		sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)


class JavaServerPlus(mcstatus.JavaServer):
	"""
	1. Remove retries
	2. Perform status + ping in one connection
	"""

	async def async_status_plus(self, *, ctx: ProbeContext) -> JavaStatusResponse:
		async with TCPAsyncSocketConnectionPlus(self.address, self.timeout, proxy=ctx.proxy) as connection:
			return await self.__do_async_status_plus(connection, ctx=ctx)

	async def __do_async_status_plus(self, connection: TCPAsyncSocketConnection, *, ctx: ProbeContext) -> JavaStatusResponse:
		if ctx.mimic:
			ping_address = Address.parse_address(ctx.mimic)
		else:
			ping_address = self.address
		pinger = AsyncServerPinger(connection, address=ping_address)

		pinger.handshake()
		result = await pinger.read_status()

		if result.motd:
			# the icon request might be costly, so perform another ping request to get the real ping
			logger.debug('Performing another ping request to get the real ping')
			result.latency = await pinger.test_ping()

		return result


class BedrockServerPlus(BedrockServer):
	"""
	1. Remove retries
	"""
	@override
	async def async_status(self, **kwargs) -> BedrockStatusResponse:
		return await BedrockServerStatus(self.address, self.timeout).read_status_async()
