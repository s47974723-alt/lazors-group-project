import copy
import time
from PIL import Image, ImageDraw, ImageFont
from sympy.utilities.iterables import multiset_permutations
from parser import parse_bff
from blocks import GridBuilder, find_occupied_spots, obvious_skip
from tracer import LazorTracer


# ============================================================
# Path finding and block placement search
# ============================================================
def path_seek(grid, num_a, num_b, num_c, lazor_list, hole_list, position):
    """
    Try all possible combinations of A, B, C blocks in available 'o' cells.
    Return the first configuration that allows all lazors to hit their targets.
    """

    # Collect all open positions ('o') that can hold a block
    blocks = []
    for row in grid:
        for element in row:
            if element == 'o':
                blocks.append(element)

    # Replace the first n open cells with A/B/C according to counts
    for i in range(num_a):
        blocks[i] = 'A'
    for i in range(num_a, (num_a + num_b)):
        blocks[i] = 'B'
    for i in range((num_a + num_b), (num_a + num_b + num_c)):
        blocks[i] = 'C'

    # Generate all unique permutations of these blocks
    block_permutations = list(multiset_permutations(blocks))

    # Try each permutation one by one
    while len(block_permutations) != 0:
        blocks_temp = block_permutations[-1]
        blocks_temp_save = copy.deepcopy(blocks_temp)
        block_permutations.pop()

        # Create a new board with this block configuration
        original_grid = GridBuilder(grid)
        test_board = original_grid.generate_grid(blocks_temp, position)

        # Skip configurations that can be ruled out early (for efficiency)
        if obvious_skip(test_board, block_permutations, blocks_temp, hole_list):
            lazor = LazorTracer(test_board, lazor_list, hole_list)
            solution = lazor.lazor_path()

            # If this configuration successfully hits all holes, return it
            if solution != 0:
                return solution, blocks_temp_save, test_board
            else:
                continue


# ============================================================
# Solver main function
# ============================================================
def solver(fptr):
    """
    Solve a given .bff puzzle file and generate both text and image outputs.
    """

    # 1. Parse the .bff file using our parser
    data = parse_bff(fptr)
    grid = data[0]          # Full grid (expanded)
    num_a = data[1]         # Number of A (reflect) blocks
    num_b = data[2]         # Number of B (opaque) blocks
    num_c = data[3]         # Number of C (refract) blocks
    lazors = data[4]        # Lazor start points and directions
    holes = data[5]         # Target points
    small_grid = data[6]    # Original non-expanded grid

    # 2. Find occupied (unavailable) and open positions
    occupied_spots = find_occupied_spots(small_grid)

    # 3. Solve the puzzle using path_seek()
    solution, lazor_path = path_seek(grid, num_a, num_b, num_c,
                                     lazors, holes, occupied_spots)[:2]

    # 4. Create a new grid with the chosen blocks inserted
    new_grid = copy.deepcopy(small_grid)
    lazor_index = 0
    for row in range(len(new_grid)):
        for col in range(len(new_grid[0])):
            if new_grid[row][col] == 'o':
                new_grid[row][col] = lazor_path[lazor_index]
                lazor_index += 1

    # 5. Print a readable text solution in terminal
    print(f"\n=== Solution for {fptr} ===")
    print("Final board configuration:")
    for line in new_grid:
        print(' '.join(line))
    print("\nBlock placement order:", lazor_path)
    print("----------------------------")

    # 6. Generate the solved puzzle image
    image_output(solved_board=new_grid, answer_lazor=solution,
                 lazor_info=lazors, holes=holes, filename=fptr)

    # 7. Summary
    output_filename = '.'.join(fptr.split('.')[0:-1])
    print(f"The puzzle has been solved and saved as {output_filename}_solved.png")

    return new_grid, solution, lazor_path


# ============================================================
# Block colors for visualization
# ============================================================
def solution_color():
    """
    Define RGB colors for each grid symbol.
    """
    return {
        0: (200, 200, 200),   # default
        'A': (255, 255, 255), # white - reflective
        'B': (50, 50, 50),    # dark gray - opaque
        'C': (180, 0, 180),   # purple - refractive
        'o': (150, 150, 150), # light gray - open slot
        'x': (100, 100, 100), # dark gray - blocked
    }


# ============================================================
# Visualization: draw the grid, lazors, and targets
# ============================================================
def image_output(solved_board, answer_lazor, lazor_info, holes, filename, block_size=50):
    """
    Draw the final solved board as an image.
    """
    n_blocks_y = len(solved_board)
    n_blocks_x = len(solved_board[0])
    dim_x = n_blocks_x * block_size
    dim_y = n_blocks_y * block_size

    # Create a blank image
    img = Image.new("RGB", (dim_x, dim_y), color=(140, 140, 140))
    draw = ImageDraw.Draw(img)

    colors = solution_color()

    # Load font for block labels
    font_size = max(12, block_size // 3)
    try:
        font = ImageFont.truetype("arial.ttf", font_size)
    except IOError:
        font = ImageFont.load_default()

    # Draw the grid and blocks
    for jy in range(n_blocks_y):
        for jx in range(n_blocks_x):
            ch = solved_board[jy][jx]
            color = colors.get(ch, (200, 200, 200))
            x0, y0 = jx * block_size, jy * block_size
            x1, y1 = x0 + block_size, y0 + block_size
            draw.rectangle([x0, y0, x1, y1], fill=color, outline=(100, 100, 100), width=1)

            # Label blocks A/B/C in the center
            if ch in ('A', 'B', 'C'):
                bbox = draw.textbbox((0, 0), ch, font=font)
                tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
                cx, cy = (x0 + x1) // 2, (y0 + y1) // 2
                fg = (255, 255, 255) if ch == 'B' else (0, 0, 0)
                draw.text((cx - tw // 2, cy - th // 2), ch, fill=fg, font=font)

    # Draw lazor start points (red dots)
    r = max(3, block_size // 10)
    for sx, sy, _, _ in lazor_info:
        px, py = sx * block_size / 2.0, sy * block_size / 2.0
        draw.ellipse([px - r, py - r, px + r, py + r],
                     fill=(255, 0, 0), outline=(255, 0, 0))

    # Draw lazor paths (red lines)
    for path in answer_lazor:
        for i in range(len(path) - 1):
            x0, y0 = path[i][0] * block_size / 2.0, path[i][1] * block_size / 2.0
            x1, y1 = path[i + 1][0] * block_size / 2.0, path[i + 1][1] * block_size / 2.0
            draw.line([(x0, y0), (x1, y1)], fill=(255, 0, 0), width=4)

    # Draw hole (target) positions
    for hx, hy in holes:
        px, py = hx * block_size / 2.0, hy * block_size / 2.0
        draw.ellipse([px - r, py - r, px + r, py + r],
                     fill=(255, 255, 255), outline="red", width=2)

    # Save image with _solved suffix
    out = filename
    if out.endswith(".bff"):
        out = out[:-4] + "_solved.png"
    elif not out.lower().endswith(".png"):
        out = out + "_solved.png"
    img.save(out)


# ============================================================
# Main execution: solve multiple puzzles and time the process
# ============================================================
if __name__ == "__main__":
    t0 = time.time()

    puzzles = [
        'showstopper_4.bff', 'tiny_5.bff', 'mad_7.bff',
        'dark_1.bff', 'mad_1.bff', 'mad_4.bff',
        'numbered_6.bff', 'yarn_5.bff'
    ]
    for p in puzzles:
        solver(p)

    t1 = time.time()
    print(f"\nAll puzzles solved in {t1 - t0:.2f} seconds.")
