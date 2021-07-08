from xmlrpc.client import ServerProxy
from threading import Lock
from functools import lru_cache
import logging


@lru_cache(maxsize=8)
def get_ni_client(addr):
    return NI660XRPCClient(addr)


class NI660XRPCClient:
    def __init__(self, addr):
        self._proxy = ServerProxy(addr)
        self._lock = Lock()

    def __getattr__(self, item):
        def func(*args, **kwargs):
            logging.info('NI client enter %s', item)
            with self._lock:
                result = getattr(self._proxy, item)(*args, **kwargs)
                logging.info('NI client return %s', item)
                return result

        func.__name__ = item
        setattr(self, item, func)
        return func

