from typing import List, Tuple, Dict
import re

# Type aliases for readability
Grid = List[List[str]]
BlockCounts = Dict[str, int]
Lazor = Tuple[int, int, int, int]
Point = Tuple[int, int]


def parse_bff(path: str) -> Tuple[Grid, BlockCounts, List[Laser], List[Point]]:
    """
    parse .bff file
    output: (grid, block_counts, lasers, targets)

    """
    grid: Grid = []
    block_counts: BlockCounts = {'A': 0, 'B': 0, 'C': 0}
    lazors: List[Laser] = []
    targets: List[Point] = []

    try:
        with open(path, 'r', encoding='utf-8') as f:
            lines = [ln.rstrip('\n') for ln in f]
    except FileNotFoundError as e:
        raise FileNotFoundError(f"Cannot open the file: {path}") from e

    in_grid = False
    for raw in lines:
        if raw is None:
            continue
        line = raw.strip()
        # Ignore empty lines or comment lines
        if not line or line.startswith('#'):
            continue

        # GRID START / STOP control
        tokens = line.split()
        if len(tokens) >= 2 and tokens[0].upper() == 'GRID' and tokens[1].upper() == 'START':
            in_grid = True
            continue
        if len(tokens) >= 2 and tokens[0].upper() == 'GRID' and tokens[1].upper() == 'STOP':
            in_grid = False
            continue

        if in_grid:
            # Split by spaces
            row_tokens = line.split()
            if len(row_tokens) == 0:
                continue
            # Standardize characters, keep 'o', 'x'
            norm_row = [tok.upper() if tok.lower() not in ('o','x') else tok.lower() for tok in row_tokens]
            grid.append(norm_row)
            continue

        # Analysis A/B/C count, L, P
        key = tokens[0].upper()

        # A/B/C counts: format "A 2" or "B 1"
        if key in ('A', 'B', 'C'):
            if len(tokens) >= 2:
                try:
                    block_counts[key] = int(tokens[1])
                except ValueError:
                    # If it cannot be converted into integer, ignore it and keep the default 0
                    block_counts[key] = 0
            continue

        # Lazor line L x y vx vy
        if key == 'L':
            # Find all integers
            nums = [int(x) for x in re.findall(r'-?\d+', line)]
            if len(nums) >= 4:
                x, y, vx, vy = nums[0], nums[1], nums[2], nums[3]
                lazors.append((x, y, vx, vy))
            # If less than 4, ignore
            continue

        # Target Point P x y
        if key == 'P':
            nums = [int(x) for x in re.findall(r'-?\d+', line)]
            if len(nums) >= 2:
                x, y = nums[0], nums[1]
                targets.append((x, y))
            continue

    # Verify the consistent number of rows and columns of the grid
    if grid:
        row_len = len(grid[0])
        for r in grid:
            if len(r) != row_len:
                raise ValueError("Error. Please check the .bff file.")

    return grid, block_counts, lasers, targets

def grid_size(grid: Grid) -> Tuple[int, int]:
    """
    Return the (cols, rows) of grid
    """
    rows = len(grid)
    cols = len(grid[0]) if rows > 0 else 0
    return cols, rows


def valid_place_positions(grid: Grid) -> List[Point]:
    """
    Return a list of positions (x, y) on the grid where the blocks can be placed
    'o' is placeable, 'x' is prohibited
    If the grid contains 'A''B''C', they are considered fixed blocks and cannot be placed
    """
    cols, rows = grid_size(grid)
    poss: List[Point] = []
    for y in range(rows):
        for x in range(cols):
            val = grid[y][x]
            if isinstance(val, str) and val.lower() == 'o':
                poss.append((x, y))
    return poss


def get_fixed_blocks(grid: Grid) -> Dict[Point, str]:
    """
    Scan the grid and return fixed mapping
    """
    cols, rows = grid_size(grid)
    fixed = {}
    for y in range(rows):
        for x in range(cols):
            v = grid[y][x]
            if isinstance(v, str) and v.upper() in ('A', 'B', 'C'):
                fixed[(x, y)] = v.upper()
    return fixed



# If run this file, make a simple self test
if __name__ == "__main__":
    import argparse, pprint
    parser = argparse.ArgumentParser(description="self test parser.py")
    parser.add_argument("bff", help=".bff file road")
    args = parser.parse_args()

    grid, bc, lasers, targets = parse_bff(args.bff)
    print("GRID:")
    for row in grid:
        print(" ".join(row))
    print("block_counts:", bc)
    print("lazors:", lasers)
    print("targets:", targets)
    print("valid place positions:", valid_place_positions(grid))
    print("fixed blocks:", get_fixed_blocks(grid))

