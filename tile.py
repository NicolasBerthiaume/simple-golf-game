from enum import Enum, auto

class TileType(Enum):
    ROUGH = auto()
    GREEN = auto()
    WATER = auto()
    SAND = auto()
    TEE = auto()
    HOLE = auto()

class Tile:
    def __init__(self, x, y, type = TileType.ROUGH):
        self.x = x
        self.y = y
        self.type = type