import mcstatus
from mcstatus.pinger import ServerPinger
from mcstatus.protocol.connection import TCPSocketConnection
from mcstatus.status_response import JavaStatusResponse
from mcstatus.utils import retry
from typing_extensions import override, Callable

from blackcraft_exporter.logger import get_logger


class JavaServerPlus(mcstatus.JavaServer):
	"""
	Perform status + ping in one connection
	"""
	@override
	def status(self, timeout_getter: Callable[[], float]) -> JavaStatusResponse:
		return super().status(timeout_getter=timeout_getter)

	@override
	@retry(tries=3)
	def _retry_status(self, connection: TCPSocketConnection, *, timeout_getter: Callable[[], float]) -> JavaStatusResponse:
		logger = get_logger()
		pinger = ServerPinger(connection, address=self.address)

		def update_timeout():
			connection.socket.settimeout(timeout_getter())

		update_timeout()
		pinger.handshake()

		update_timeout()
		result = pinger.read_status()

		if result.motd:
			# the icon request might be costly, perform another ping request to get the real ping
			logger.debug('Performing another ping request to get the real ping')
			update_timeout()
			result.latency = pinger.test_ping()
		return result