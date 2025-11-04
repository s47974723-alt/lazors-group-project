# This module is used to simulate the propagation, reflection, refraction and hitting of the laser on the Lazor chessboard, as well as the target point.
from typing import List, Union, Optional

Coord = List[int]     # [x, y]
Ray   = List[int]     # [x, y, dx, dy]
Grid  = List[List[str]]


class LazorTracer:
    # Trace Lazor rays across an expanded half-grid puzzle board.
    def __init__(self, grid: Grid, lazor_list: List[Ray], hole_list: List[Coord]):
        self.grid = grid
        self.lazor_list = lazor_list
        self.hole_list = hole_list

        # Scratch state set immediately before each interaction
        self.point: Optional[Coord] = None     # current lattice point being processed
        self.direction: Optional[Coord] = None # current incoming direction [dx, dy]

    # Defines how a ray interacts with different block types and updates its direction accordingly.
    def trace_block_interaction(self, block_type: str) -> List[int]:
        
        # Calculate the new ray direction(s) after interacting with a given block type.
        assert self.point is not None and self.direction is not None
        x = self.point[0]
        dx, dy = self.direction

        if block_type == 'A':                        # Reflect
            return [-dx, dy] if x % 2 == 0 else [dx, -dy]
        if block_type == 'B':                        # Opaque
            return []
        if block_type == 'C':                        # Refract
            return [dx, dy, -dx, dy] if x % 2 == 0 else [dx, dy, dx, -dy]
        if block_type in ('o', 'x'):                 # Empty / no-placement cell
            return [dx, dy]
        return []                                    # Unknown → absorb (safe default)

    # Check whether the ray's current or next position goes outside the grid boundaries.
    def is_out_of_bounds(self, coord: Coord, direction: Optional[Coord]) -> bool:
       
       # Check if the current ray position or its next step is outside the grid.
        w, h = len(self.grid[0]), len(self.grid)
        x, y = coord
        if direction is None:
            return True
        nx, ny = x + direction[0], y + direction[1]
        return not (0 <= x < w and 0 <= y < h and 0 <= nx < w and 0 <= ny < h)

    # The main loop that advances all lazor rays step by step until all targets are hit or the limit is reached.
    def trace_all_paths(self, max_steps: int = 50) -> Union[int, List[List[Ray]]]:
        
        # Simulate all lazor paths step-by-step until all targets are hit or the step limit is reached.
        # 'hit' bookkeeping: store unique coordinates visited that match holes
        hits: List[Coord] = []

        # Initialize per-ray path lists with given starting states
        lazor_paths: List[List[Ray]] = [[lz] for lz in self.lazor_list]

        for _ in range(max_steps):
            # Iterate over a snapshot of current paths (paths may grow during loop)
            for i in range(len(lazor_paths)):
                x, y, dx, dy = lazor_paths[i][-1]
                coord = [x, y]
                direction = [dx, dy]

                # If this step would go out, we drop the ray silently
                if self.is_out_of_bounds(coord, direction):
                    continue

                # Compute outgoing direction(s) based on the neighbor we hit next
                next_dirs = self.compute_reflection(coord, direction)

                if not next_dirs:
                    # Absorbed at current coord (record terminal state)
                    lazor_paths[i].append([x, y, 0, 0])
                    if coord in self.hole_list and coord not in hits:
                        hits.append(coord)

                elif len(next_dirs) == 2:
                    # Single outgoing ray
                    ndx, ndy = next_dirs
                    nx, ny = x + ndx, y + ndy
                    lazor_paths[i].append([nx, ny, ndx, ndy])
                    if [nx, ny] in self.hole_list and [nx, ny] not in hits:
                        hits.append([nx, ny])

                elif len(next_dirs) == 4:
                    # Refract: split into two rays
                    ndx1, ndy1, ndx2, ndy2 = next_dirs
                    nx1, ny1 = x + ndx1, y + ndy1   # spawned branch
                    nx2, ny2 = x, y                 # original path continues from same node

                    # New branch starts its own path list
                    lazor_paths.append([[nx1, ny1, ndx1, ndy1]])

                    # Original path follows the second branch
                    lazor_paths[i].append([nx2, ny2, ndx2, ndy2])

                    if [nx2, ny2] in self.hole_list and [nx2, ny2] not in hits:
                        hits.append([nx2, ny2])

                # else: unrecognized shape → ignore this step

            # Success condition: all holes have been hit at least once
            if len(hits) == len(self.hole_list):
                return lazor_paths

        # Not all holes were hit within the step budget
        return 0

    # Determine which neighboring cell the ray hits and compute its resulting direction(s).
    def compute_reflection(self, point: Coord, direction: Coord) -> List[int]:
    
        # Identify the next neighbor cell hit and compute the resulting outgoing direction(s) based on half-grid parity.
        self.point = point
        self.direction = direction

        # Candidate neighbors
        x1, y1 = point[0],               point[1] + direction[1]  # vertical neighbor (same x, moved in y)
        x2, y2 = point[0] + direction[0], point[1]                # horizontal neighbor (moved in x, same y)

        if point[0] % 2 == 1:  # odd x → vertical neighbor gets hit
            block_type = self.grid[y1][x1]
        else:                  # even x → horizontal neighbor gets hit
            block_type = self.grid[y2][x2]

        return self.trace_block_interaction(block_type)

    # Provides old method names as aliases to maintain compatibility with previous solver code.
    def block(self, block_type: str) -> List[int]:
        return self.trace_block_interaction(block_type)

    def check_position(self, coord: Coord, direction: Optional[Coord]) -> bool:
        return self.is_out_of_bounds(coord, direction)

    def lazor_path(self, max_steps: int = 50) -> Union[int, List[List[Ray]]]:
        return self.trace_all_paths(max_steps=max_steps)

    def block_reflect(self, point: Coord, direction: Coord) -> List[int]:
        return self.compute_reflection(point, direction)
