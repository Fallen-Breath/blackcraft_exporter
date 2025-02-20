import contextlib
import dataclasses
import time
from typing import Any, Generator, Optional

from prometheus_client import CollectorRegistry, Gauge


@dataclasses.dataclass
class ProbeContext:
	registry: CollectorRegistry
	target: str
	timeout: Optional[float]

	def gauge(self, name: str, doc: str, *, labels: Optional[dict[str, str]] = None) -> Gauge:
		gauge = Gauge(name=name, documentation=doc, registry=self.registry, labelnames=(labels or {}).keys())
		if labels:
			gauge = gauge.labels(**labels)
		return gauge

	@contextlib.contextmanager
	def time_cost_gauge(self, name: str, doc: str) -> Generator[Gauge, Any, None]:
		start = time.time()
		gauge = Gauge(name=name, documentation=doc, registry=self.registry)
		try:
			yield gauge
		finally:
			gauge.set(time.time() - start)
