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

## 2. block module (block.py)

The block module defines behavior of each block type in lazor game.
  - A-reflect block: reflects the lazor
  - B-opaque block: absorbs the lazor
  - C-refract block: reflects + transmits

## 3. tracer module (tracer.py)

The tracer module implements the lazor simulation engine for the Lazor game.
It is responsible for tracking laser movement through the grid, determining interactions with different block types, and identifying whether all target points are reached.

### Main Functions:
 - in_bounds_half(pt, rows, cols): Checks if a half-cell coordinate is within the board boundary.
 - cells_touched_by_step(curr, d): Determines which block cells a laser may cross when moving one step.
 - _apply_block(block, direction, hit_side): Applies block-specific behavior (reflection, absorption, or refraction).
 - trace_single(...): Traces the path of a single laser beam, including reflections and splits.
 - trace_all(...): Runs simulation for all lazors (including branches created by “C” blocks) and collects results such as hit points and full paths.

### Behavior Rules:
 - A (Reflect block): Reflects the lazor by flipping its direction according to which side it hits.
 - B (Opaque block): Absorbs the lazor and terminates its path.
 - C (Refract block): Splits the lazor into two paths — one reflected and one transmitted.
The simulation stops when the lazor exits the grid or is absorbed by a B block.

# Group members and contribution:
- Zhikuang Yan: parser, block modules
- Ziyu Peng: tracer module — implemented the laser physics engine, multi-lazor tracing, reflection/refraction logic, and integrated unit tests for verification.
