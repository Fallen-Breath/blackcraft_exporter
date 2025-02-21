import mcstatus
from mcstatus import BedrockServer
from mcstatus.bedrock_status import BedrockServerStatus
from mcstatus.pinger import ServerPinger
from mcstatus.protocol.connection import TCPSocketConnection
from mcstatus.status_response import JavaStatusResponse, BedrockStatusResponse
from typing_extensions import override

from blackcraft_exporter.logger import get_logger


class JavaServerPlus(mcstatus.JavaServer):
	"""
	Remove retries; Perform status + ping in one connection
	"""
	@override
	def _retry_status(self, connection: TCPSocketConnection, **kwargs) -> JavaStatusResponse:
		logger = get_logger()
		pinger = ServerPinger(connection, address=self.address)

		def update_timeout():
			connection.socket.settimeout(kwargs['timeout_getter']())

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


class BedrockServerPlus(BedrockServer):
	"""
	Remove retries
	"""
	@override
	def status(self, **kwargs) -> BedrockStatusResponse:
		return BedrockServerStatus(self.address, self.timeout).read_status()
