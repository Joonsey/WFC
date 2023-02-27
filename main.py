import random
import time

class Cell:
    def __init__(self) -> None:
        self.options: list[int] = [1,2,3,4,5,6,7,8,9]
        self.collapsed: bool = False

    @property
    def entropy(self) -> int:
        return len(self.options)

    def collapse(self) -> int:
        self.collapsed = True
        self.options = [self.options[random.randrange(self.entropy)]]
        return self.options[0]

class WFC:
    def __init__(self, x, y) -> None:
        self.x, self.y = x, y
        self.cells: list[list[Cell]] = [[]]

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

        if x < self.x-1:
            self.propogate(1+x, y, option)
        if 0 < x:
            self.propogate(x-1, y, option)
        if y < self.y-1:
            self.propogate(x, 1+y, option)
        if 0 < y:
            self.propogate(x, y-1, option)

    def propogate(self, x, y, option):
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

if __name__ == "__main__":
    wfc = WFC(9,9)
    wfc.build_cells()
    wfc.collapse(2,2)

    while not wfc.all_collapsed:
        cell_with_least_entropy = wfc.find_least_entropy()
        cell_location = wfc.find_cell_location(cell_with_least_entropy)
        wfc.collapse(cell_location[0], cell_location[1])

        for line in wfc.get_entropies():
            print(line)

        print("\n")
        time.sleep(.1)
