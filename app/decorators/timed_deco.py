import functools
import time
from typing import Callable, Any
from app.logger import get_log

log = get_log()


def timed(func: Callable) -> Callable:
    """Measure elapsed time of asynchronous functions execution."""
    @functools.wraps(func)
    async def wrapped(*args, **kwargs) -> Any:
        start_time = time.time()
        try:
            res = await func(*args, **kwargs)

            elapsed_time = time.time() - start_time
            log.debug("Executed=%s, module=%s, elapsed_time=%s, args=%s, kwargs=%s, res=%s." % (
                str(func), func.__module__, elapsed_time, str(args), str(kwargs), str(res)))

            return res
        except Exception as e:
            raise e

    return wrapped
