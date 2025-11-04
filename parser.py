"""
blocks.py

Helper functions for Lazor grid and block placement.

- Grid_part: update grid when placing blocks
- find_occupied_spots: find fixed A/B/C blocks
- obvious_skip: skip clearly invalid configurations
"""

class Grid_part:
    """
    Manage grid updates when placing blocks.
    """

    def __init__(self, original_grid):
        """
        Initialize the grid.
        original_grid : list[list[str]]
            2D grid from .bff file
        """
        self.original_grid = original_grid
        self.length = len(original_grid)
        self.width = len(original_grid[0])
        self.list_grid = None

    def generate_grid(self, list_grid, position):
        """
        Place blocks into the grid
        list_grid : list[str]
            blocks to place
        position : list[list[int]]
            valid positions
        """
        self.list_grid = list_grid
        for row in range(self.length):
            for column in range(self.width):
                # Skip fixed or invalid spots
                if [row, column] not in position:
                    if self.original_grid[row][column] != 'x' and list_grid:
                        self.original_grid[row][column] = list_grid.pop(0)
        return self.original_grid


def find_occupied_spots(small_grid):
    """
    Return positions of fixed A/B/C blocks in expanded grid
    """
    positions = []
    for i in range(len(small_grid)):
        for j in range(len(small_grid[0])):
            if small_grid[i][j] in ['A', 'B', 'C']:
                positions.append([i * 2 + 1, j * 2 + 1])
    return positions


def obvious_skip(grid, possibles, lst, holes):
    """
    Skip setups where targets are blocked by A/B blocks
    """
    for x0, y0 in holes:
        x, y = y0, x0
        try:
            if ((grid[x][y + 1] in ['A', 'B']) and (grid[x][y - 1] in ['A', 'B'])) or \
               ((grid[x + 1][y] in ['A', 'B']) and (grid[x - 1][y] in ['A', 'B'])):
                return False
            else:
                return True
        except IndexError:
            continue
    return True
