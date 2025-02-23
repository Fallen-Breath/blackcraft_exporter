import asyncio
import contextlib
import dataclasses
import time
from typing import Any, Generator, Optional, TypeVar, Awaitable, Callable, List

from prometheus_client import CollectorRegistry, Gauge
from websockets.asyncio import async_timeout

from blackcraft_exporter import utils
from blackcraft_exporter.constants import PROMETHEUS_METRIC_NAMESPACE

_T = TypeVar('_T')

class RetryExceptionGroup(ExceptionGroup):
	def __str__(self):
		exceptions_str = ', '.join(f'({type(e)}) {e}' for e in self.exceptions)
		return f'{self.message}: {exceptions_str}'

	def all_failures_are_timeout(self) -> bool:
		return all(map(utils.is_timeout_exception, self.exceptions))


@dataclasses.dataclass(frozen=True)
class ProbeContext:
	registry: CollectorRegistry
	target: str
	timeout: float
	mimic: Optional[str]
	proxy: Optional[str]
	max_attempts: int

	__start_time: float = dataclasses.field(default_factory=time.time)

	def get_timeout_remaining(self) -> float:
		return max(0.0, self.timeout - (time.time() - self.__start_time))

	def gauge(self, name: str, doc: str, *, labels: Optional[dict[str, str]] = None) -> Gauge:
		gauge = Gauge(
			name=name,
			namespace=PROMETHEUS_METRIC_NAMESPACE,
			documentation=doc,
			registry=self.registry,
			labelnames=(labels or {}).keys(),
		)
		if labels:
			gauge = gauge.labels(**labels)
		return gauge

	@contextlib.contextmanager
	def time_cost_gauge(self, name: str, doc: str) -> Generator[Gauge, Any, None]:
		start = time.time()
		gauge = self.gauge(name=name, doc=doc)
		try:
			yield gauge
		finally:
			gauge.set(time.time() - start)

	@contextlib.asynccontextmanager
	async def timeout_guard(self):
		async with async_timeout.timeout(self.timeout):
			yield

	async def do_with_timeout_and_retries(self, func: Callable[[], Awaitable[_T]]) -> _T:
		errors: List[Exception] = []
		async with self.timeout_guard():
			for attempt in range(self.max_attempts):
				async with async_timeout.timeout(self.timeout / self.max_attempts):
					try:
						return await func()
					except asyncio.CancelledError:
						raise
					except Exception as e:
						errors.append(e)
		raise RetryExceptionGroup(f'All {self.max_attempts} attempts failed', errors)
