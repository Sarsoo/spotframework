from dataclasses import fields
from unittest.mock import Mock

def create_dataclass_mock(obj):
    return Mock(spec=[field.name for field in fields(obj)], __class__ = obj)