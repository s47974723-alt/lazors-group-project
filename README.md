# Lazor Group Project - Hello World

## Project Goal
This project aims to automatically solve Lazor puzzles by reading `.bff` files, simulating lazor paths with different block types (reflect, opaque, refract), and generating clear visual outputs of the solved boards.

## How to Run

1. Download all 4 main Python modules:
   - `parser.py`
   - `blocks.py`
   - `tracer.py`
   - `solver.py`

2. Download the `.bff` example files and place them in the same project folder.

3. Run the solver: > python solver.py

4. The solved board images will be generated in the same directory.


## Project Structure

## 1. parser module (parser.py)

The parser reads .bff file and converts text into data structure required by solver, including:
 - Grid layout and valid block positions
 - Number of movable blocks (A, B, C)
 - Lazor starting coordinates and directions
 - Target points to be hit by lazors

Return: 
- grid_full: Expanded grid (with inserted 'x' separators)
- num_a/b/c_blocks: Number of 3 types of blocks (A/B/C) 
- lazor_start: Lazors start points [x, y, vx, vy]
- end_point_positions: Target coordinates [x, y]
- raw_grid: Original grid from .bff file

## 2. block module (blocks.py)

This module manages grid updates and block placement for the Lazor solver and provides functions to handle how blocks (A, B, C) are placed and to skip invalid setups.

### Main Functions:
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

## 4. solver module (solver.py)
The solver module integrates all components to find and display the final Lazor solution. It loads the puzzle from a .bff file, enumerates valid A/B/C block placements, simulates laser movement for each configuration, and outputs both an image and a text summary of the result.
### Main Functions:
 - solver(fptr) – Entry point that reads the .bff, determines available block positions, calls path_seek(...) to test possible layouts, prints the solution grid, and saves the solved image.
 - path_seek(...) – Generates all unique block permutations (A/B/C), builds boards via GridBuilder.generate_grid(...), prunes invalid layouts with obvious_skip(...), and validates success      through LazorTracer.lazor_path(...).
 - image_output(...) – Draws the final board with labeled blocks, red laser paths and start points, and white target holes; saves as {filename}_solved.png.
### Final Output Presentation:
 - Text (Terminal): Displays the solved board as a grid of characters (A/B/C/x/o), followed by the sequence of block placements and a completion message showing the generated image name.
 - Image (Visual): The .png output provides a complete visual verification — fixed and movable blocks are labeled, red lines show lazor paths, red dots mark starting points, and white          circles outline target holes that have been successfully hit.
# Group members and contribution:
- Zhikuang Yan: parser module and block module
- Ziyu Peng: tracer module — implemented the laser physics engine, multi-lazor tracing, reflection/refraction logic.
- Tsunghan Lin: solver module
