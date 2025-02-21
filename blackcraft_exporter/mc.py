import mcstatus
from mcstatus.pinger import AsyncServerPinger
from mcstatus.protocol.connection import TCPAsyncSocketConnection
from mcstatus.status_response import JavaStatusResponse
from mcstatus.utils import retry
from typing_extensions import override

from blackcraft_exporter.logger import get_logger


class JavaServerPlus(mcstatus.JavaServer):
	"""
	Perform status + ping in one connection
	"""
	@override
	@retry(tries=3)
	async def _retry_async_status(self, connection: TCPAsyncSocketConnection, **kwargs) -> JavaStatusResponse:
		logger = get_logger()
		pinger = AsyncServerPinger(connection, address=self.address, **kwargs)
		pinger.handshake()
		result = await pinger.read_status()
		if result.motd:
			# the icon request might be costly, perform another ping request to get the real ping
			logger.debug('Performing another ping request to get the real ping')
			result.latency = await pinger.test_ping()
		return result