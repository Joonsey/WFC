#!/bin/python
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

# 1 = DARK BLUE TILE
# 2 = PARTIAL DARK / LIGHT BLUE TILE
# 3 = LIGHT GREEN TILE
# 4 = PARTIAL LIGHT GREEN DARK GRAY TILE
# 5 = DARK GRAY TILE

basic_tile = Tile("4", ['bbb', 'aaa', 'aaa', 'aaa'])
dark_blue_tile = Tile("1", ['ddd', 'ddd', 'ddd', 'ddd'])

TILE_TABLE = {
    1 : basic_tile,
    2 : basic_tile.rotate(),
    3 : basic_tile.rotate().rotate(),
    4 : basic_tile.rotate().rotate().rotate(),
    5 : basic_tile.rotate().rotate().rotate(),
    6 : Tile("1", ['ddd', 'aaa', 'ddd', 'aaa']),
    7 : Tile("5", ['bbb', 'bbb', 'bbb', 'bbb']),
    8 : Tile("2", ['ddd', 'ddd', 'ccc', 'ddd']),
    9 : Tile("2", ['ddd', 'aaa', 'ccc', 'aaa']),
    10 : Tile("3", ['ccc', 'aaa', 'aaa', 'aaa']),
    11 : Tile("3", ['aaa', 'aaa', 'aaa', 'aaa']),
    12 : dark_blue_tile,
}

def inverse(socket: str):
    return socket[2]+socket[1]+socket[0]

def foo(selected):
    all_options = []
    for option in TILE_TABLE.keys():
        tile = TILE_TABLE[option]
        if tile.sockets[3] == selected.sockets[1]:
            all_options.append(option)
    return all_options


class Cell:
    def __init__(self) -> None:
        self.options: list[int] = list(TILE_TABLE.keys())
        self.collapsed: bool = False
        self.tile: None | Tile = None

    @property
    def entropy(self) -> int:
        return len(self.options)

    def collapse(self, override: int= 0) -> int:
        self.collapsed = True
        if override:
            self.options = [override]
        else:
            print("options", self.options)
            self.options = [random.choice(self.options)]
            print("choice:", self.options)
        self.tile = TILE_TABLE[self.options[0]]
        return self.options[0]

    def validate(self, selected:Tile, direction : str):
        options = self.options.copy()
        #options = TILE_TABLE.keys()
        if direction == "right":
            self.options = (list(filter(lambda x : TILE_TABLE[x].sockets[1] in selected.sockets[3], options)))
        if direction == "left":
            self.options = (list(filter(lambda x : TILE_TABLE[x].sockets[3] in selected.sockets[1], options)))
        if direction == "above":
            self.options = (list(filter(lambda x : TILE_TABLE[x].sockets[0] in selected.sockets[2], options)))
        if direction == "below":
            self.options = (list(filter(lambda x : TILE_TABLE[x].sockets[2] in selected.sockets[0], options)))

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

    def collapse(self, x, y, override:int = 0):
        assert x < self.x and y < self.y, \
            "x and y must be smaller than the dimensions of the list of cells"

        cell = self.cell_at(x,y)
        if override:
            option = cell.collapse(override)
        else:
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
    wfc = WFC(28,20)
    display = pygame.display.set_mode((1080,720))
    smol_surf = pygame.surface.Surface((8*wfc.x, 8*wfc.y))
    wfc.build_cells()
    wfc.collapse(0,0, 6)


    while not wfc.all_collapsed:
        display.fill(0)
        cell_with_least_entropy = wfc.find_least_entropy()
        cell_location = wfc.find_cell_location(cell_with_least_entropy)
        wfc.collapse(cell_location[0],cell_location[1])

        for y in range(len(wfc.cells)):
            for x in range(len(wfc.cells[y])):
                cell = wfc.cell_at(x, y)
                if cell.tile != None:
                    smol_surf.blit(cell.tile.surf, (x*8, y*8))

        pygame.transform.rotate(smol_surf, 180)
        pygame.transform.scale(smol_surf, (1080,720), display)
        pygame.display.update()
        time.sleep(.01)

def run():
    while True:
        try:
            main()
        except IndexError:
            continue

if __name__ == "__main__":
    run()


