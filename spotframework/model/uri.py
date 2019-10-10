from enum import Enum


class Uri:

    class ObjectType(Enum):
        track = 1
        album = 2
        artist = 3
        user = 4
        playlist = 5

    def __init__(self, input_string: str):
        self.object_type = None
        self.object_id = None
        self.username = None
        self.is_local = False

        parts = input_string.split(':')

        if parts[0] != 'spotify':
            raise ValueError('malformed uri')

        if len(parts) == 3:
            self.object_type = self.ObjectType[parts[1]]
            self.object_id = parts[2]
        elif len(parts) == 5:
            if parts[1] != 'user':
                raise ValueError('malformed uri')
            self.object_type = self.ObjectType[parts[3]]
            self.object_id = parts[4]
        elif len(parts) == 6:
            if parts[1] == 'local':
                self.object_type = self.ObjectType.track
                self.is_local = True
            else:
                raise ValueError(f'malformed uri: {len(parts)} parts')
        else:
            raise ValueError(f'malformed uri: {len(parts)} parts')

    def __str__(self):
        if self.username:
            return f'spotify:user:{self.username}:{self.object_type.name}:{self.object_id}'
        else:
            return f'spotify:{self.object_type.name}:{self.object_id}'

    def __repr__(self):
        if self.username:
            return f'URI: {self.username} / {self.object_type.name} / {self.object_id}'
        else:
            return f'URI: {self.object_type.name} / {self.object_id}'

    def __eq__(self, other):
        if isinstance(other, Uri):
            if other.object_type == self.object_type and other.object_id == self.object_id:
                return True

        return False

