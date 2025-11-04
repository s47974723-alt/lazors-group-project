# Lazor Group Project - Hello World

## Project Structure

## 1. parser module (parser.py)

The parser reads .bff file and converts text into data structure required by solver, including:
 - Grid layout and valid block positions
 - Number of movable blocks (A, B, C)
 - Lazor starting coordinates and directions
 - Target points to be hit by lazors

Return: 
- grid_full: Expanded grid (with inserted 'x' separators)
- num_a/b/c_blocks: Number of reflect (A/B/C) blocks
- lazor_start: Lazors start points [x, y, vx, vy]
- end_point_positions: Target coordinates [x, y]
- raw_grid: Original grid from .bff file

## 2. block module (blocks.py)

This module manages grid updates and block placement for the Lazor solver and provides functions to handle how blocks (A, B, C) are placed and to skip invalid setups.
  - Grid_part – Updates the grid when new blocks are placed.
  - find_occupied_spots() – Finds fixed A/B/C block positions in the grid.
  - obvious_skip() – Skips configurations where holes are blocked by A/B blocks.

## 3. tracer module (tracer.py)

This module simulates lazor (laser) paths on the Lazor half-grid board. It handles block interactions (reflect/absorb/refract), boundary checks, and reports whether all target holes are hit.

### Main Functions:
 - trace_all_paths() – Main simulation loop; traces all lazor rays step-by-step until all targets are hit or the step limit is reached.
 - compute_reflection() – Determines which neighboring block the lazor strikes next and computes the new outgoing direction(s).
 - trace_block_interaction() – Defines how each block type (A, B, C, o, x) affects the lazor (reflection, absorption, refraction, or straight-through).
 - is_out_of_bounds() – Checks if the lazor’s next position goes beyond the grid boundary.

### Behavior Rules:
 - A (Reflect block): Reflects the lazor by flipping its direction according to which side it hits.
 - B (Opaque block): Absorbs the lazor and terminates its path.
 - C (Refract block): Splits the lazor into two paths — one reflected and one transmitted.
The simulation stops when the lazor exits the grid or is absorbed by a B block.

# Group members and contribution:
- Zhikuang Yan: parser, block modules
- Ziyu Peng: tracer module — implemented the laser physics engine, multi-lazor tracing, reflection/refraction logic.
