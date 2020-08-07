import math
from spotframework.model.uri import Uri


def convert_ms_to_minute_string(ms):
    seconds = ms / 1000
    minutes = math.floor(seconds / 60)

    return f'{minutes}:{math.floor(seconds%60)}'


def validate_uri_string(uri_string: str):
    try:
        uri = Uri(uri_string)
        return uri
    except ValueError:
        return False

def get_uri(uri_in):

    if isinstance(uri_in, str):
        return Uri(input_string=uri_in)

    if isinstance(uri_in, Uri):
        return uri_in

    raise TypeError(f'invalid uri type provided - {type(uri_in)}')
