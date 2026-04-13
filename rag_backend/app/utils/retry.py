from collections.abc import Callable
from time import sleep
from typing import TypeVar

from app.core.errors import AppError

T = TypeVar("T")


def retry_call(
    operation: Callable[[], T],
    *,
    attempts: int,
    delay_seconds: float,
    error_message: str,
    error_code: str,
    status_code: int = 502,
) -> T:
    last_exception: Exception | None = None
    for attempt in range(1, attempts + 1):
        try:
            return operation()
        except Exception as exc:  # noqa: PERF203
            last_exception = exc
            if attempt == attempts:
                break
            sleep(delay_seconds)

    raise AppError(
        message=f"{error_message}: {last_exception}",
        status_code=status_code,
        code=error_code,
    ) from last_exception
