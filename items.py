from dataclasses import dataclass
from typing import Any


@dataclass(slots=True)
class Post:
    """ represents a profile. """
    index: int = None
    post_type: str = None
    body: str = None
    media_file_path: str = None
    upload_date: str = None
    bot_username: str = None
    __attrs__ = ["post_type", "body", "media_file_path", "upload_date", "bot_username"]

    def items(self) -> list[tuple]:
        """ returns all items in the object as a tuple. """
        return [(attr, self.get(attr)) for attr in Post.__attrs__]

    def get(self, key: str) -> Any:
        """ returns an attribute of the object. """
        return self.__getitem__(str(key))

    def __getitem__(self, item: str) -> Any:
        return getattr(self, str(item))

    def __setitem__(self, key: str, value: Any) -> Any:
        return setattr(self, str(key), value)

    def __add__(self, other):
        return Post(**dict(self.items() + other.items()))
