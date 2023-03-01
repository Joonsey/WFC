from __future__ import annotations
import random
import time
import pygame

pygame.init()

ASSET_PATH = "tiles/"


class Tile:
    def __init__(self, name: str, sockets: list[str], surf:pygame.surface.Surface | None = None) -> None:
        self.name = name
        self.sockets = sockets
        if surf == None:
            self.surf = pygame.image.load(ASSET_PATH + name + ".png")
        else:
            self.surf = surf

    def rotate(self) -> Tile:
        new_sockets: list[str] = []
        surf = pygame.transform.rotate(self.surf, 90)
        for i in range(len(self.sockets.copy())):
            new_sockets.append(self.sockets[i-1])

        return Tile(self.name, new_sockets, surf)

    def __str__(self) -> str:
        return str(self.sockets)


# A = LIGHT GREEN
# B = DARK GRAY
# C = DARK GREEN / LIGHT BLUE
# D = DARK BLUE

basic_tile = Tile("4", ['bbb', 'aaa', 'aaa', 'aaa'])
TILE_TABLE = {
    1 : basic_tile,
    2 : basic_tile.rotate(),
    3 : basic_tile.rotate().rotate(),
    4 : basic_tile.rotate().rotate().rotate(),
    5 : basic_tile.rotate().rotate().rotate(),
    6 : Tile("1", ['ddd', 'ddd', 'ddd', 'ddd']),
    7 : Tile("5", ['bbb', 'bbb', 'bbb', 'bbb']),
    8 : Tile("2", ['ddd', 'ddd', 'ccc', 'ddd']),
    9 : Tile("3", ['aaa', 'aaa', 'aaa', 'aaa']),
}

def inverse(socket: str):
    return socket[2]+socket[1]+socket[0]

class Cell:
    def __init__(self) -> None:
        self.options: list[int] = list(TILE_TABLE.keys())
        self.collapsed: bool = False
        self.tile: None | Tile = None

    @property
    def entropy(self) -> int:
        return len(self.options)

    def collapse(self) -> int:
        self.collapsed = True
        self.options = [random.choice(self.options)]
        self.tile = TILE_TABLE[self.options[0]]
        return self.options[0]


    def validate(self, selected:Tile, direction : str):
        if direction == "right":
            self.options = (list(filter(lambda x : inverse(TILE_TABLE[x].sockets[3]) == selected.sockets[1], self.options)))
        if direction == "left":
            self.options = (list(filter(lambda x : inverse(TILE_TABLE[x].sockets[1]) == selected.sockets[3], self.options)))
        if direction == "up":
            self.options = (list(filter(lambda x : inverse(TILE_TABLE[x].sockets[2]) == selected.sockets[0], self.options)))
        if direction == "down":
            self.options = (list(filter(lambda x : inverse(TILE_TABLE[x].sockets[0]) == selected.sockets[2], self.options)))

class WFC:
    def __init__(self, x, y) -> None:
        self.x, self.y = x, y
        self.cells: list[list[Cell]] = [[]]

    def get_collapsed(self) -> list[Cell]:
        all_cells = []
        [all_cells.extend(copy_list) for copy_list in self.cells.copy()]
        return list(filter(lambda x: x.collapsed, all_cells))


    @property
    def all_collapsed(self) -> bool:
        all_cells = []
        [all_cells.extend(copy_list) for copy_list in self.cells.copy()]
        return all([cell.collapsed for cell in all_cells])

    def cell_at(self, x, y) -> Cell:
        assert x <= self.x and y <= self.y, \
            "x and y must be smaller than the dimensions of the list of cells"
        return self.cells[y][x]

    def build_cells(self) -> None:
        self.cells = [[Cell() for x in range(self.x)] for _ in range(self.y)]

    def collapse(self, x, y):
        assert x < self.x and y < self.y, \
            "x and y must be smaller than the dimensions of the list of cells"

        cell = self.cell_at(x,y)
        option = cell.collapse()

        self.propogate(x, y, option)

    def propogate(self, x:int, y:int, option:int):
        if x < self.x-1:
            self.cell_at(x+1, y).validate(TILE_TABLE[option], "right")
        if 0 < x:
            self.cell_at(x-1, y).validate(TILE_TABLE[option], "left")
        if y < self.y-1:
            self.cell_at(x, y+1).validate(TILE_TABLE[option], "above")
        if 0 < y:
            self.cell_at(x, y-1).validate(TILE_TABLE[option], "below")

        cell = self.cell_at(x, y)
        if option in cell.options:
            cell.options.remove(option)

    def get_entropies(self) -> list[list[int]]:
        return [[cell.entropy for cell in cells] for cells in self.cells]

    def find_cell_location(self, cell : Cell) -> tuple[int, int]:
        x, y = -1, -1
        for l in self.cells:
            if cell in l:
                x = l.index(cell)
                y = self.cells.index(l)

        assert x != -1 and y != -1, "reference to cell not found in WFC.cells"
        return x, y

    def find_least_entropy(self) -> Cell:
        all = []
        [all.extend(copy_list) for copy_list in self.cells.copy()]

        only_non_collapsed = list(filter(lambda x: not x.collapsed, all))
        only_non_collapsed.sort(key = lambda x: x.entropy)

        lowest_entropy = only_non_collapsed[0].entropy
        all_lowest_entropies = list(filter(lambda x: x.entropy == lowest_entropy and not x.collapsed, only_non_collapsed))
        return all_lowest_entropies[random.randrange(len(all_lowest_entropies))]


def main():
    wfc = WFC(9,9)
    wfc.build_cells()
    wfc.collapse(2,2)

    display = pygame.display.set_mode((500,600))
    smol_surf = pygame.surface.Surface((8*wfc.x, 8*wfc.y))

    while not wfc.all_collapsed:
        cell_with_least_entropy = wfc.find_least_entropy()
        cell_location = wfc.find_cell_location(cell_with_least_entropy)
        wfc.collapse(cell_location[0],cell_location[1])

        for y in range(len(wfc.cells)):
            for x in range(len(wfc.cells[y])):
                cell = wfc.cell_at(x, y)
                if cell.tile != None:
                    smol_surf.blit(cell.tile.surf, (x*8, y*8))

        pygame.transform.scale(smol_surf, (500,600), display)
        display.blit(smol_surf, (0,0))
        pygame.display.update()
        time.sleep(.1)

if __name__ == "__main__":
    main()
