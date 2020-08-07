import functools
import logging

from collections.abc import Iterable

from spotframework.util import get_uri
from spotframework.model.uri import Uri

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

def inject_uri(_func=None, *, uri=True, uris=True, flatten_to_uris=False, uri_optional=False, uris_optional=False):

    def decorator_inject_uri(func):
        @functools.wraps(func)
        def inject_uri_wrapper(*args, **kwargs):

            if uri:
                if uri_optional:
                    if flatten_to_uris:
                        kwargs['uris'] = [ get_uri(kwargs['uri']) ] if kwargs.get('uri') else None
                    else:
                        kwargs['uri'] = get_uri(kwargs['uri']) if kwargs.get('uri') else None
                else:
                    if flatten_to_uris:
                        kwargs['uris'] = [ get_uri(kwargs['uri']) ]
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

def contain_uri_types(types_in):

    if isinstance(types_in, Iterable):
        for uri_type in types_in:
            if not isinstance(uri_type, Uri.ObjectType):
                raise TypeError(f'provided type not a uri object type, {type(uri_type)}')
        types = types_in

    elif isinstance(types_in, Uri.ObjectType):
        types = [types_in]

    else:
        raise TypeError(f'provided type not a uri object type, {type(types_in)}')

    return types

def uri_type_check(uri_type = None, uris_type = None):
    def decorator_type_check(func):
        @functools.wraps(func)
        def wrapper_type_check(*args, **kwargs):
            if uri_type is not None:
                if kwargs['uri'].object_type not in contain_uri_types(uri_type):
                    raise TypeError(f'uri not of required type {uri_type}, {kwargs["uri"].object_type}')

            if uris_type is not None:
                for uri in kwargs['uris']:
                    if uri.object_type not in contain_uri_types(uris_type):
                        raise TypeError(f'uri not of required type {uris_type}, {uri.object_type}')

            return func(*args, **kwargs)
        return wrapper_type_check
    return decorator_type_check
