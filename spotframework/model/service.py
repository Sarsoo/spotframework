from dataclasses import dataclass


@dataclass
class Image:
    height: int
    width: int
    url: str

    @staticmethod
    def wrap(**kwargs):
        return Image(**kwargs)
