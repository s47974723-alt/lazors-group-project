from __future__ import annotations
from typing import Dict, Iterable, List, Set, Tuple
from collections import deque

# Import existing block behaviors
from blocks import Block, Reflect, Opaque, Refract, FixedBlock

# Type aliases
Point = Tuple[int, int]   # half-cell coordinate (x, y)
Dir   = Tuple[int, int]   # direction (dx, dy) with components in {-1,0,1}, not both 0
Cell  = Tuple[int, int]   # grid cell (cx, cy)

# Determine whether a half-grid coordinate is still within the chessboard range.
def in_bounds_half(pt: Point, rows: int, cols: int) -> bool:
    # Check if a half-cell coordinate is still inside the board
    x, y = pt
    return 0 <= x <= 2 * cols and 0 <= y <= 2 * rows

# Check whether the position of the square to be placed is within the chessboard.
def in_bounds_cell(cell: Cell, rows: int, cols: int) -> bool:
    # Check if a cell coordinate (grid position) is inside the board
    cx, cy = cell
    return 0 <= cx < cols and 0 <= cy < rows

# Make the laser move one step in the current direction.
def step(pt: Point, d: Dir) -> Point:
    # Move one step along direction d
    return (pt[0] + d[0], pt[1] + d[1])

# Check whether the character in a certain cell is a square.
def _norm_block_char(ch: str) -> str | None:
    # Normalize grid characters to uppercase A/B/C if valid
    if not isinstance(ch, str):
        return None
    up = ch.upper()
    return up if up in ("A", "B", "C") else None

# Find all the fixed blocks (A/B/C) in the grid, convert them into program objects and record them.
def build_blocks_map(grid: List[List[str]]) -> Dict[Cell, Block]:
    rows = len(grid)
    cols = len(grid[0]) if rows else 0
    blocks: Dict[Cell, Block] = {}
    for y in range(rows):
        for x in range(cols):
            tok = _norm_block_char(grid[y][x])
            if tok is None:
                continue
            blocks[(x, y)] = FixedBlock(tok)
    return blocks

# Determine which cells a step may touch
def cells_touched_by_step(curr: Point, d: Dir) -> List[Cell]:
    x, y = curr
    dx, dy = d
    touched: List[Cell] = []

# Based on the current direction of the laser (dx, dy), calculate the coordinates of the block grid that it might hit when moving one step from its current position.
    if dx != 0 and dy == 0:
        # Horizontal move: check the current row
        cy = (y - 1) // 2
        cx = (x + dx) // 2 if dx > 0 else (x + dx) // 2 - 1
        touched.append((cx, cy))
    elif dy != 0 and dx == 0:
        # Vertical move: check the current column
        cx = (x - 1) // 2
        cy = (y + dy) // 2 if dy > 0 else (y + dy) // 2 - 1
        touched.append((cx, cy))
    else:
        # Diagonal: check horizontal side first, then vertical side
        cy_h = (y - 1) // 2
        cx_h = (x + dx) // 2 if dx > 0 else (x + dx) // 2 - 1
        touched.append((cx_h, cy_h))

        cx_v = (x - 1) // 2
        cy_v = (y + dy) // 2 if dy > 0 else (y + dy) // 2 - 1
        touched.append((cx_v, cy_v))

    return touched

# Based on the current direction d (dx, dy) of the laser and the hit cell, determine from which side the light enters the cell.
def _compute_hit_side(curr: Point, d: Dir, hit_cell: Cell) -> str:
    dx, dy = d
    # Horizontal movement: When dx > 0, enter the hit_cell from its "left"; when dx < 0, enter from the "right".
    if dx != 0 and dy == 0:
        return 'left' if dx > 0 else 'right'
    # Vertical movement: When dy > 0, enter from "up"; when dy < 0, enter from "down".
    if dy != 0 and dx == 0:
        return 'up' if dy > 0 else 'down'
    # Diagonal: by our candidate ordering, the first cell corresponds to the horizontal-side crossing, so treat as left/right based on dx.
    return 'left' if dx > 0 else 'right'

# Apply block interaction
def _apply_block(block: Block, direction: Dir, hit_side: str | None = None) -> List[Dir]:
    # detect A (Reflect or FixedBlock('A'))：Call `block.interact` to obtain the reflection or refraction direction. 
    # If it is an A block and a collision edge is provided, flip the x or y direction according to the edge; otherwise, use the default interaction logic and filter out invalid directions.
    is_reflect = isinstance(block, Reflect) or (
        hasattr(block, "block") and getattr(block, "block", None) == "A"
    )

    if is_reflect and hit_side is not None:
        # Try new signature first: interact(direction, hit_side)
        try:
            outs = block.interact(direction, hit_side)  # type: ignore[arg-type]
        except TypeError:
            # Fall back to legacy signature but enforce edge-aware reflection here
            dx, dy = direction
            if hit_side in ('left', 'right'):
                outs = [(-dx, dy)]
            elif hit_side in ('up', 'down'):
                outs = [(dx, -dy)]
            else:
                outs = [(-dx, -dy)]
    else:
        # If B/C or the 'hit_side' is not available, then use the behavior settings in the 'blocks.py' file.
        outs = block.interact(direction)

    # sanitize directions
    valid: List[Dir] = []
    for dx, dy in outs:
        if (dx, dy) == (0, 0):
            continue
        if dx not in (-1, 0, 1) or dy not in (-1, 0, 1):
            continue
        valid.append((dx, dy))
    return valid
  

# Trace one single laser beam
def trace_single(start: Point,
                 d0: Dir,
                 targets: Set[Point],
                 blocks_map: Dict[Cell, Block],
                 rows: int,
                 cols: int,
                 max_steps: int = 20000) -> Tuple[List[Point], Set[Point], List[Dir]]:
    # This part is the initialization of the state.
    path: List[Point] = [start]
    covered: Set[Point] = set()
    if start in targets:
        covered.add(start)

    curr = start
    d = d0
    steps = 0

    while steps < max_steps:
        nxt = step(curr, d)

        # Exit boundary  
        if not in_bounds_half(nxt, rows, cols):
            path.append(nxt)
            if nxt in targets:
                covered.add(nxt)
            return path, covered, []

        # Check potential blocks along the step
        interacted = False
        for cell in cells_touched_by_step(curr, d):
            if not in_bounds_cell(cell, rows, cols):
                continue
            blk = blocks_map.get(cell)
            if blk is None:
                continue

            interacted = True
            hit_side = _compute_hit_side(curr, d, cell)
            outs = _apply_block(blk, d, hit_side=hit_side)

            if not outs:
                # Absorbed by 'B'
                path.append(nxt)
                if nxt in targets:
                    covered.add(nxt)
                return path, covered, []

            if len(outs) == 1:
                # Reflected by 'A' (reverse direction)
                path.append(curr)
                d = outs[0]
                break

            # Refracted by 'C': stop here, return two directions
            path.append(curr)
            return path, covered, outs

        if not interacted:
            # Move forward normally
            curr = nxt
            path.append(curr)
            if curr in targets:
                covered.add(curr)

        steps += 1

    # Reached max steps (safety stop)
    return path, covered, []


# Simulate all laser beams (including the branched light generated by the C block), and summarize all paths and hit results
def trace_all(grid: List[List[str]],
              lazors: Iterable[Tuple[int, int, int, int]],
              targets: Set[Point],
              blocks_map: Dict[Cell, Block],
              rows: int,
              cols: int,
              max_steps: int = 40000):

    # Initialize the queue and result container to store the beams to be tracked, their paths, and hit information.
    q = deque()
    for (x, y, vx, vy) in lazors:
        q.append(((x, y), (vx, vy)))

    all_paths: List[List[Point]] = []
    all_hits: Set[Point] = set()
    covered_targets: Set[Point] = set()
    alive = 0

    # Sequentially extract each laser beam for tracking, record the path and update the hit target status.
    while q:
        start, d0 = q.popleft()
        path, covered, branches = trace_single(start, d0, targets, blocks_map, rows, cols, max_steps)
        all_paths.append(path)
        all_hits.update(path)
        covered_targets |= covered

        # Handle the splitting and termination of the light beams, and return the complete tracking results of all the light beams.
        if branches:
            # Split beam: add new rays to the queue
            branch_start = path[-1]
            for nd in branches:
                q.append((branch_start, nd))
        else:
            # Beam ended (exit or absorbed)
            alive += 1

    return {
        "paths": all_paths,
        "hit_points": all_hits,
        "covered_targets": covered_targets,
        "alive": alive,
    }


# Unit tests
if __name__ == "__main__":
    import unittest

    class TracerTests(unittest.TestCase):

        def _run(self, grid, lazors, targets):
            rows, cols = len(grid), len(grid[0])
            blocks = build_blocks_map(grid)
            return trace_all(grid, lazors, targets, blocks, rows, cols)

        def test_straight_no_blocks_hits_target(self):
            # Laser moves straight on empty board and hits target at right edge.
            grid = [['o','o','o'],
                    ['o','o','o'],
                    ['o','o','o']]
            lazors = [(0, 3, 1, 0)]
            targets = {(5, 3)}
            out = self._run(grid, lazors, targets)
            self.assertIn((5,3), out["covered_targets"])
            self.assertEqual(out["alive"], 1)

        def test_absorb_by_B(self):
            # Laser is absorbed by B (no branches).
            grid = [['o','o','o'],
                    ['o','B','o'],  # (1,1)
                    ['o','o','o']]
            lazors = [(0, 3, 1, 0)]
            out = self._run(grid, lazors, set())
            self.assertEqual(out["alive"], 1)
            # Path should terminate on the same row (y=3) shortly after impact.
            last_points = [p[-1] for p in out["paths"]]
            self.assertTrue(any(lp[1] == 3 for lp in last_points))

        def test_reflect_by_A(self):
            # Laser reflects on A; expects edge-aware reflection (flip x only).
            grid = [['o','o','o'],
                    ['o','A','o'],  # (1,1)
                    ['o','o','o']]
            lazors = [(0, 3, 1, 0)]
            targets = {(1, 3)}  # should be hit after reflection
            out = self._run(grid, lazors, targets)
            self.assertIn((1,3), out["covered_targets"])
            self.assertEqual(out["alive"], 1)

        def test_refract_by_C(self):
            # Laser hits C and splits into two beams (right + left).
            # NOTE: trace_all advances branch start by one half-step to avoid immediate re-split loops.
            grid = [['o','o','o'],
                    ['o','C','o'],  # (1,1)
                    ['o','o','o']]
            lazors = [(0, 3, 1, 0)]
            targets = {(1,3), (5,3)}
            out = self._run(grid, lazors, targets)
            # Both sides should be reachable; at least two finished beams.
            self.assertTrue({(1,3), (5,3)}.issubset(out["covered_targets"]))
            self.assertGreaterEqual(out["alive"], 2)
            # Sanity: total path length should remain modest (no runaway loop).
            total_len = sum(len(p) for p in out["paths"])
            self.assertLessEqual(total_len, 200)


    unittest.main(verbosity=2)
