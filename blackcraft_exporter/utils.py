from urllib.parse import urlparse


def validate_ip_port(ip_port: str, needs_port: bool) -> bool:
	url = urlparse("//" + ip_port)
	try:
		_ = url.port  # validate port if it exists
		if needs_port and url.port is None:
			return False
		return url.netloc == ip_port and bool(url.hostname)
	except ValueError:
		return False
