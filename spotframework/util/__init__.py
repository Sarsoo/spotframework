import math


def convert_ms_to_minute_string(ms):
    seconds = ms / 1000
    minutes = math.floor(seconds / 60)

    return f'{minutes}:{math.floor(seconds%60)}'
