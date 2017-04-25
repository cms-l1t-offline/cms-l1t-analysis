from __future__ import print_function
import time
import functools


def __timerfunc(func, printer=None):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        """
        A function for timing other functions
        """
        start = time.time()
        value = func(*args, **kwargs)
        end = time.time()
        runtime = end - start
        msg = "The runtime for {func} took {time} seconds to complete"
        printer(msg.format(func=func.__name__,
                           time=runtime))
        return value
    wrapper.__wrapped__ = func
    return wrapper


def timerfunc(func):
    """
    A timer decorator that prints to stdout
    """
    function_timer = functools.partial(__timerfunc, printer=print)(func)
    return function_timer


def timerfunc_log_to(printer):
    """
    A timer decorator that prints to a specific print function or logger
    """
    function_timer = functools.partial(__timerfunc, printer=printer)
    return function_timer
