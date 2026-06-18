"""Thread pool for CPU-bound work."""

from concurrent.futures import ThreadPoolExecutor

_executor = ThreadPoolExecutor(max_workers=4)


def get_executor() -> ThreadPoolExecutor:
    return _executor
