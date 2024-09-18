from enum import Enum

class TokenState(Enum):
    NONE = 0
    REQUEST = 1
    SC = 2
    RELEASED = 3