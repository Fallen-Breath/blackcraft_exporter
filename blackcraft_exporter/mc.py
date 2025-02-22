import socket

import mcstatus
from mcstatus import BedrockServer
from mcstatus.bedrock_status import BedrockServerStatus
from mcstatus.pinger import AsyncServerPinger
from mcstatus.protocol.connection import TCPAsyncSocketConnection
from mcstatus.status_response import JavaStatusResponse, BedrockStatusResponse
from typing_extensions import override

from blackcraft_exporter.logger import get_logger


class TCPAsyncSocketConnectionPlus(TCPAsyncSocketConnection):
	"""
	Apply TCP_NODELAY to the socket
	"""
	async def connect(self) -> None:
		await super().connect()
		sock = self.writer.transport.get_extra_info('socket')
		sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)


class JavaServerPlus(mcstatus.JavaServer):
	"""
	Remove retries; Perform status + ping in one connection
	"""
	async def async_status(self, **kwargs) -> JavaStatusResponse:
		async with TCPAsyncSocketConnectionPlus(self.address, self.timeout) as connection:
			return await self._retry_async_status(connection, **kwargs)

	@override
	async def _retry_async_status(self, connection: TCPAsyncSocketConnection, **kwargs) -> JavaStatusResponse:
		logger = get_logger()

		pinger = AsyncServerPinger(connection, address=self.address)
		pinger.handshake()
		result = await pinger.read_status()

		if result.motd:
			# the icon request might be costly, perform another ping request to get the real ping
			logger.debug('Performing another ping request to get the real ping')
			result.latency = await pinger.test_ping()

		return result


class BedrockServerPlus(BedrockServer):
	"""
	Remove retries
	"""
	@override
	async def async_status(self, **kwargs) -> BedrockStatusResponse:
		return await BedrockServerStatus(self.address, self.timeout).read_status_async()
