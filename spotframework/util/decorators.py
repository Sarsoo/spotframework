import functools
import logging

from spotframework.util import get_uri

logger = logging.getLogger(__name__)


def debug(func):
    @functools.wraps(func)
    def wrapper_debug(*args, **kwargs):
        args_repr = [repr(a) for a in args]
        kwargs_repr = [f"{k}={v!r}" for k, v in kwargs.items()]
        signature = ", ".join(args_repr + kwargs_repr)
        print(f"{func.__name__}({signature})")
        value = func(*args, **kwargs)
        print(f"{func.__name__!r} -> {value!r}")
        return value
    return wrapper_debug

def inject_uri(_func=None, *, uri=True, uris=True, uri_optional=False, uris_optional=False):

    def decorator_inject_uri(func):
        @functools.wraps(func)
        def inject_uri_wrapper(*args, **kwargs):
            if uri:
                if uri_optional:
                    kwargs['uri'] = get_uri(kwargs['uri']) if kwargs.get('uri') else None
                else:
                    kwargs['uri'] = get_uri(kwargs['uri'])

            if uris:
                if uris_optional:
                    kwargs['uris'] = [get_uri(i) for i in kwargs['uris']] if kwargs.get('uris') else None
                else:
                    kwargs['uris'] = [get_uri(i) for i in kwargs['uris']]

            return func(*args, **kwargs)

        return inject_uri_wrapper

    if _func is None:
        return decorator_inject_uri
    else:
        return decorator_inject_uri(_func)

