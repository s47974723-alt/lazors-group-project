# Lazor Group Project - Hello World

## Project Structure

## 1. parser module (parser.py)

The parser reads .bff file and converts text into data structure required by solver, including:
 - Board grid (o-exmpty and block can be placed, x-block cannot be placed)
 - Number of placeable block types (A, B, C)
 - Lazor sources and their vectors
 - Target points
 - Valid place positions

### Output data example (dark_1.bff):
  GRID:
  x o o
  o o o
  o o x
  block_counts: {'A': 0, 'B': 3, 'C': 0}
  lazors: [(3, 0, -1, 1), (1, 6, 1, -1), (3, 6, -1, -1), (4, 3, 1, -1)]
  targets: [(0, 3), (6, 1)]
  valid place positions: [(1, 0), (2, 0), (0, 1), (1, 1), (2, 1), (0, 2), (1, 2)]
  fixed blocks: {}

### Usage:
 python parser.py examples/dark_1.bff

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
