# solver.py
import copy
import time
from PIL import Image, ImageDraw
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
        original_grid = GridBuilder(copy.deepcopy(grid))
        test_board = original_grid.generate_grid(copy.deepcopy(blocks_temp), position)

        if obvious_skip(test_board, block_permutations, blocks_temp, hole_list):
            lazor = LazorTracer(test_board, lazor_list, hole_list)
            solution = lazor.lazor_path()
            if solution != 0:
                return solution, blocks_temp_save, test_board
            else:
                continue
    return None


def solution_color():
    return {
        0: (200, 200, 200),
        'A': (255, 255, 255),
        'B': (50, 50, 50),
        'C': (255, 0, 0),
        'o': (150, 150, 150),
        'x': (100, 100, 100),
    }


def image_output(solved_board, answer_lazor, lazor_info, holes, filename, block_size=50):
    n_blocks_x = len(solved_board[0])
    n_blocks_y = len(solved_board)
    dim_x = n_blocks_x * block_size
    dim_y = n_blocks_y * block_size
    colors = solution_color()
    img = Image.new("RGB", (dim_x, dim_y), color=(0, 0, 0))
    draw = ImageDraw.Draw(img)
    for jy in range(n_blocks_y):
        for jx in range(n_blocks_x):
            color = colors[solved_board[jy][jx]]
            for i in range(block_size):
                for j in range(block_size):
                    img.putpixel((jx * block_size + i, jy * block_size + j), color)

    for i in range(len(lazor_info)):
        lazor_pos = (lazor_info[i][0], lazor_info[i][1])
        draw.ellipse([lazor_pos[0] * block_size / 2 - 10, lazor_pos[1] * block_size / 2 - 10,
                      lazor_pos[0] * block_size / 2 + 10, lazor_pos[1] * block_size / 2 + 10], fill=(255, 0, 0))
    for i in answer_lazor:
        for point in range(len(i) - 1):
            co_start = (i[point][0] * block_size / 2, i[point][1] * block_size / 2)
            co_end = (i[point + 1][0] * block_size / 2, i[point + 1][1] * block_size / 2)
            draw.line([co_start, co_end], fill=(255, 0, 0), width=5)
    for hole in holes:
        x, y = hole[0] * block_size / 2, hole[1] * block_size / 2
        draw.ellipse([x - 10, y - 10, x + 10, y + 10], fill=(255, 255, 255), outline="red", width=2)
    img.save(filename.replace('.bff', '_solved.png'))


def solver(fptr):
    grid, num_a, num_b, num_c, lazors, holes, small_grid = parse_bff(fptr)
    occupied = find_occupied_spots(small_grid)
    result_tuple = path_seek(grid, num_a, num_b, num_c, lazors, holes, occupied)
    if result_tuple is None:
        print(f"No valid solution for {fptr}")
        return
    result, blocks_used, test_board = result_tuple
    image_output(small_grid, result, lazors, holes, fptr)
    print(f"Solved {fptr}")


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
