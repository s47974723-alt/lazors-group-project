# Lazor Group Project - Hello World

# Project Structure

# 1. parse module (parser.py)

The parser reads .bff file and converts text into data structure required by solver, including:
 - Board grid (0-exmpty and block can be placed, x-block cannot be placed)
 - Number of placeable block types (A, B, C)
 - Lazor sources and their vectors
 - Target points
 - Valid place positions

Output data example (dark_1.bff):
  GRID:
  x o o
  o o o
  o o x
  block_counts: {'A': 0, 'B': 3, 'C': 0}
  lazors: [(3, 0, -1, 1), (1, 6, 1, -1), (3, 6, -1, -1), (4, 3, 1, -1)]
  targets: [(0, 3), (6, 1)]
  valid place positions: [(1, 0), (2, 0), (0, 1), (1, 1), (2, 1), (0, 2), (1, 2)]
  fixed blocks: {}

Usage:
python parser.py examples/dark_1.bff

# 2. block module (block.py)

The block module defines behavior of each block type in lazor game.
  - A-reflect block: reflects the lazor
  - B-opaque block: absorbs the lazor
  - C-refract block: reflects + transmits
