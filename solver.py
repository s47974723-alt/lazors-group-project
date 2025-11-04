import copy
import time
from PIL import Image, ImageDraw, ImageFont
from sympy.utilities.iterables import multiset_permutations
from parser import parse_bff
from blocks import GridBuilder, find_occupied_spots, obvious_skip
from tracer import LazorTracer


def path_seek(grid, num_a, num_b, num_c, lazor_list, hole_list, position):
    blocks = []
    for row in grid:
        for element in row:
            if element == 'o':
                blocks.append(element)
    for i in range(num_a):
        blocks[i] = 'A'
    for i in range(num_a, (num_a + num_b)):
        blocks[i] = 'B'
    for i in range((num_a + num_b), (num_a + num_b + num_c)):
        blocks[i] = 'C'

    block_permutations = list(multiset_permutations(blocks))

    while len(block_permutations) != 0:
        blocks_temp = block_permutations[-1]
        blocks_temp_save = copy.deepcopy(blocks_temp)
        block_permutations.pop()
        original_grid = GridBuilder(grid)
        test_board = original_grid.generate_grid(blocks_temp, position)

        if obvious_skip(test_board, block_permutations, blocks_temp, hole_list):
            lazor = LazorTracer(test_board, lazor_list, hole_list)
            solution = lazor.lazor_path()
            if solution != 0:
                return solution, blocks_temp_save, test_board
            else:
                continue

def solver(fptr):
    data = parse_bff(fptr)
    grid = data[0]
    num_cols = data[1]
    num_rows = data[2]
    num_holes = data[3]
    lazors = data[4]
    holes = data[5]
    small_grid = data[6]

    # Find the positions of the occupied spots in the grid
    occupied_spots = find_occupied_spots(small_grid)

    # Solve the puzzle and find the path of the lazors
    solution, lazor_path = path_seek(grid, num_cols, num_rows, num_holes, lazors, holes, occupied_spots)[:2]

    # Create a new grid with the lazors and holes
    new_grid = copy.deepcopy(small_grid)
    lazor_index = 0
    for row in range(len(new_grid)):
        for col in range(len(new_grid[0])):
            if new_grid[row][col] == 'o':
                new_grid[row][col] = lazor_path[lazor_index]
                lazor_index += 1

    # Generate output image
    image_output(solved_board=new_grid, answer_lazor=solution, lazor_info=lazors,
                 holes=holes, filename=fptr)
    output_filename = '.'.join(fptr.split('.')[0:-1])
    print('The puzzle has been solved and saved as {}'.format(
        output_filename + '_solved.png'))
    return new_grid, solution, lazor_path

def solution_color():
    return {
        0: (200, 200, 200),
        'A': (255, 255, 255),
        'B': (50, 50, 50),
        'C': (180, 0, 180),
        'o': (150, 150, 150),
        'x': (100, 100, 100),
    }


def image_output(solved_board, answer_lazor, lazor_info, holes, filename, block_size=50):

    n_blocks_y = len(solved_board)
    n_blocks_x = len(solved_board[0])
    dim_x = n_blocks_x * block_size
    dim_y = n_blocks_y * block_size


    img = Image.new("RGB", (dim_x, dim_y), color=(140, 140, 140))
    draw = ImageDraw.Draw(img)

    colors = solution_color()


    font_size = max(12, block_size // 3)
    try:
        font = ImageFont.truetype("arial.ttf", font_size)
    except IOError:
        font = ImageFont.load_default()

    for jy in range(n_blocks_y):
        for jx in range(n_blocks_x):
            ch = solved_board[jy][jx]              
            color = colors.get(ch, (200, 200, 200))
            x0, y0 = jx * block_size, jy * block_size
            x1, y1 = x0 + block_size, y0 + block_size
            draw.rectangle([x0, y0, x1, y1], fill=color, outline=(100, 100, 100), width=1)
            if ch in ('A', 'B', 'C'):
                bbox = draw.textbbox((0, 0), ch, font=font)
                tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
                cx, cy = (x0 + x1) // 2, (y0 + y1) // 2
                fg = (255, 255, 255) if ch == 'B' else (0, 0, 0)
                draw.text((cx - tw // 2, cy - th // 2), ch, fill=fg, font=font)

    r = max(3, block_size // 10)
    for sx, sy, _, _ in lazor_info:
        px, py = sx * block_size / 2.0, sy * block_size / 2.0
        draw.ellipse([px - r, py - r, px + r, py + r], fill=(255, 0, 0), outline=(255, 0, 0))

    for path in answer_lazor:
        for i in range(len(path) - 1):
            x0, y0 = path[i][0] * block_size / 2.0, path[i][1] * block_size / 2.0
            x1, y1 = path[i + 1][0] * block_size / 2.0, path[i + 1][1] * block_size / 2.0
            draw.line([(x0, y0), (x1, y1)], fill=(255, 0, 0), width=4)
    for hx, hy in holes:
        px, py = hx * block_size / 2.0, hy * block_size / 2.0
        draw.ellipse([px - r, py - r, px + r, py + r], fill=(255, 255, 255), outline="red", width=2)

    out = filename
    if out.endswith(".bff"):
        out = out[:-4] + "_solved.png"
    elif not out.lower().endswith(".png"):
        out = out + "_solved.png"
    img.save(out)

if __name__ == "__main__":
    t0 = time.time()
    solver('showstopper_4.bff')
    solver('tiny_5.bff')
    solver('mad_7.bff')
    solver('dark_1.bff')
    solver('mad_1.bff')
    solver('mad_4.bff')
    solver('numbered_6.bff')
    solver('yarn_5.bff')
    t1 = time.time()
    print(f"Solved in {t1 - t0:.2f} seconds")
