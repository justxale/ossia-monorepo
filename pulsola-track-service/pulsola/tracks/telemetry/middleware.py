import time
import typing
from collections.abc import Callable

from opentelemetry import metrics
from starlette.requests import Request

meter = metrics.get_meter(__name__)

req_counter = meter.create_counter(
    'http_server_requests_total', '1', 'Amount of requests'
)
req_duration = meter.create_histogram(
    'http_server_duration_ms', 'ms', 'Duration of requests'
)


async def counter_middleware(
        request: Request, call_next: Callable[..., typing.Any]
) -> typing.Any:
    response = await call_next(request)
    req_counter.add(
        1,
        {
            'method': request.method,
            'path': request.url.path,
            'status_code': str(response.status_code),
        },
    )
    return response


async def duration_middleware(
        request: Request, call_next: Callable[..., typing.Any]
) -> typing.Any:
    start_time = time.perf_counter()
    response = await call_next(request)
    duration = (time.perf_counter() - start_time) * 1000
    req_duration.record(
        duration,
        {
            'method': request.method,
            'path': request.url.path,
            'status_code': str(response.status_code),
        },
    )
    return response
