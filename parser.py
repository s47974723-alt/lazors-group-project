"""
parser.py

Read and parse Lazor .bff files.

 - Allowed and fixed block positions
 - Number of movable blocks (A, B, C)
 - Lazor starting coordinates and directions
 - Target points to be hit by lazors

Output is formatted to match the solver interface.
"""

from typing import List, Tuple

def parse_bff(file_name: str):
    """
    Parse a .bff file and return all required information.

    Parameters
    ----------
    file_name: str
        The path of the .bff file to read.

    Returns
    -------
    grid_full: list[list[str]]
        Expanded grid (with inserted 'x' separators)
    num_a_blocks: int
        Number of reflect (A) blocks
    num_b_blocks: int
        Number of opaque (B) blocks
    num_c_blocks: int
        Number of refract (C) blocks
    lazor_start: list[list[int]]
        Lazors as [x, y, vx, vy]
    end_point_positions: list[list[int]]
        Target coordinates [x, y]
    raw_grid: list[list[str]]
        Original (non-expanded) grid
    """

    # Initialize storage
    temp_grid: List[List[str]] = []
    num_a_blocks = num_b_blocks = num_c_blocks = 0
    lazor_start: List[List[int]] = []
    end_point_positions: List[List[int]] = []

    # Read all lines
    with open(file_name, "r") as f:
        lines = [line.strip() for line in f if line.strip() and not line.startswith("#")]

    # Parse contents
    i = 0
    while i < len(lines):
        line = lines[i]
        if line.upper().startswith("GRID START"):
            i += 1
            while i < len(lines) and lines[i].upper() != "GRID STOP":
                temp_grid.append([x for x in lines[i] if x != " "])
                i += 1
        elif line.startswith("A "):
            num_a_blocks = int("".join([c for c in line if c.isdigit()]) or 0)
        elif line.startswith("B "):
            num_b_blocks = int("".join([c for c in line if c.isdigit()]) or 0)
        elif line.startswith("C "):
            num_c_blocks = int("".join([c for c in line if c.isdigit()]) or 0)
        elif line.startswith("L "):
            parts = line.split()
            lazor_start.append([int(p) for p in parts[1:5]])
        elif line.startswith("P "):
            parts = line.split()
            end_point_positions.append([int(p) for p in parts[1:3]])
        i += 1

    # Build expanded grid
    raw_grid = temp_grid.copy()
    row, col = len(temp_grid), len(temp_grid[0])
    insert = ["x"] * (2 * col + 1)
    grid_full = [r[:] for r in temp_grid]
    for r in range(row):
        for c in range(col + 1):
            grid_full[r].insert(2 * c, "x")
    for r in range(row + 1):
        grid_full.insert(2 * r, insert)

    return grid_full, num_a_blocks, num_b_blocks, num_c_blocks, lazor_start, end_point_positions, raw_grid


# Self test: imple test to verify that the parser reads .bff files correctly.
if __name__ == "__main__":
    import pprint
    path = input("Enter .bff file path: ")
    result = parse_bff(path)
    pprint.pprint(result)
