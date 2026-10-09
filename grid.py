import random
from tile import Tile, TileType

class Grid():
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.coordinates = [] # a list of int tuples (x, y)
        self.tile_map = {} # a dictionary mapping coordinate tuples to a Tile object
        self.generate_coordinates()
        self.generate_tile_map()

        self.tee = None
        self.hole = None

    def generate_coordinates(self):
        for i in range(1, self.height +1):
            for j in range(1, self.width +1):
                self.coordinates.append((j, i))

    def generate_tile_map(self):
        self.tile_map = {(x, y): Tile(x, y) for x, y in self.coordinates}

    def generate_course_data(self):
        for t in self.tile_map.values():
            t.type = TileType.ROUGH
        
        self.tee = self.generate_and_return_tee()
        self.hole = self.generate_and_return_hole()
        
        for _ in range(4):
            self.generate_island(TileType.GREEN, 8, 15)
        for _ in range(2):
            self.generate_island(TileType.WATER, 5, 10)
        for _ in range(2):
            self.generate_island(TileType.SAND, 5, 10)

    def get_neighboring_tiles(self, x, y):
        neighbors = []
        for dx, dy in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
            neighbor = self.tile_map.get((x + dx, y + dy))
            if neighbor is not None:
                neighbors.append(neighbor)
        return neighbors

    def generate_island(self, type, min_size=2, max_size=4, seed=None):
        if seed is None:
            seed = self.tile_map.values()

        crawlable_tiles = [t for t in self.tile_map.values() if t.type == TileType.ROUGH]

        size = random.randint(min_size, max_size)
        current = random.choice(crawlable_tiles)
        current.type = type
        island = [current]

        for _ in range(1, size):
            neighbors = self.get_neighboring_tiles(current.x, current.y)
            candidates = [n for n in neighbors if n not in island and n.type == TileType.ROUGH]

            if not candidates:
                break

            new = random.choice(candidates)
            new.type = type
            island.append(new)
            current = new

    # generates the tee in the lower half of the grid
    # should address the magic number though
    def generate_and_return_tee(self):
        candidates = [t for (x, y), t in self.tile_map.items() if y > self.height - 5 and t.type == TileType.ROUGH]
        tee = random.choice(candidates)
        tee.type = TileType.TEE
        return tee

    # same comments as above
    def generate_and_return_hole(self):
        candidates = [t for (x, y), t in self.tile_map.items() if y <= 5]
        hole = random.choice(candidates)
        hole.type = TileType.HOLE
        return hole

    def convert_to_dict(self):
        rows = []
        for y in range(1, self.height + 1):
            rows.append([self.tile_map[(x, y)].type.name for x in range(1, self.width + 1)])

        return {
            "tiles": rows,
            "tee_pos": [self.tee.x, self.tee.y],
            "hole_pos": [self.hole.x, self.hole.y],
        }

    def convert_from_dict(self, data):
        self.generate_tile_map()

        for y, row in enumerate(data["tiles"], start=1):
            for x, type_name in enumerate(row, start=1):
                self.tile_map[(x, y)].type = TileType[type_name]

        self.tee = self.tile_map[tuple(data["tee_pos"])]
        self.hole = self.tile_map[tuple(data["hole_pos"])]