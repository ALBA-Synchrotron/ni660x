from xmlrpc.client import ServerProxy
from threading import Lock
from functools import lru_cache


@lru_cache(maxsize=8)
def get_ni_client(addr):
    return NI660XRPCClient(addr)


class NI660XRPCClient:
    def __init__(self, addr):
        self._proxy = ServerProxy(addr)
        self._lock = Lock()

    def __getattr__(self, item):
        def func(*args, **kwargs):
            with self._lock:
                return getattr(self._proxy, item)(*args, **kwargs)
        func.__name__ = item
        setattr(self, item, func)
        return func

