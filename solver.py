import sys
import itertools
import time
from typing import List, Dict, Tuple, Set

# --- Importing Your Other Code ---
# Let's grab all the helper functions and classes you already built.
try:
    from parser import parse_bff, valid_place_positions, grid_size, get_fixed_blocks, Lazor
    from blocks import Block, Reflect, Opaque, Refract, FixedBlock
    from tracer import trace_all, build_blocks_map
except ImportError as e:
    print(f"Hey, I couldn't import your other files.")
    print(f"Details: {e}")
    print("Just make sure 'parser.py', 'blocks.py', and 'tracer.py' are in the same folder as this solver.")
    sys.exit(1)


# Type Aliases (just to make the code easier to read)
Point = Tuple[int, int]
Cell = Tuple[int, int]
BlockCounts = Dict[str, int]
Laser = Tuple[int, int, int, int] # <-- This is OK, it's just an alias inside solver.py
Grid = List[List[str]]


BLOCK_PROTOTYPES = {
    'A': Reflect(),
    'B': Opaque(),
    'C': Refract()
}


def solve(grid: Grid, 
          block_counts: BlockCounts, 
          lazors: List[Lazor], 
          targets: List[Point]) -> Dict[Cell, str] | None:
    """
    This is the main brain. It tries to find a solution for the board.
    
    Returns:
        A dictionary like {(x,y): 'A', ...} if it finds a solution.
        If not, it just returns None.
    """
    
    print("Solver starting...")

    # 1. Find all the blocks that are already baked into the grid (A, B, C).
    #    We use build_blocks_map because it handily turns them into objects for us.
    fixed_blocks_map: Dict[Cell, Block] = build_blocks_map(grid)
    print(f"Found {len(fixed_blocks_map)} fixed blocks.")

    # 2. Find all the empty spots where we're *allowed* to place blocks (the 'o's).
    placements: List[Cell] = valid_place_positions(grid)
    print(f"Found {len(placements)} valid placement spots.")

    # 3. Make a simple list of all the blocks we need to place.
    #    e.g., if block_counts is {'A': 2, 'C': 1}, this list becomes ['A', 'A', 'C']
    movables: List[str] = []
    for block_type, count in block_counts.items():
        movables.extend([block_type] * count)
    
    num_movables = len(movables)
    print(f"Need to place {num_movables} blocks: {movables}")

    # --- Some quick sanity checks ---
    if num_movables == 0 and not targets:
        print("No blocks to place and no targets. Easiest puzzle ever. Solved.")
        return {} # An empty layout is a valid solution here.
    
    if num_movables > len(placements):
        print(f"Error: More blocks to place ({num_movables}) than available spots ({len(placements)}). Impossible.")
        return None

    # 4. Get the targets ready. A 'set' is way faster for checking "is this target hit?"
    target_set: Set[Point] = set(targets)
    rows, cols = grid_size(grid)

    # --- The Core Algorithm: Brute-Force Combinations ---

    # 5. Step A: Get all combinations of *positions*.
    #    "Out of 16 'o' spots, give me every possible group of 3 spots."
    spot_combinations = itertools.combinations(placements, num_movables)

    # 6. Step B: Get all unique *arrangements* of the blocks.
    #    "How many unique ways can I arrange ['A', 'A', 'C']?"
    #    Answer: ('A','A','C'), ('A','C','A'), ('C','A','A')
    #    Using a 'set' automatically handles duplicates for us.
    block_permutations = set(itertools.permutations(movables))
    print(f"Total {len(block_permutations)} unique block arrangements.")


    # 7. Time to check every single possibility. This is the main loop.
    total_checks = 0
    
    # We start with a map that just has the fixed blocks.
    # We'll add and remove the movable blocks from this map inside the loop.
    current_blocks_map = fixed_blocks_map.copy()
    
    # --- Main Loop ---
    for spot_combo in spot_combinations:
        # spot_combo is a tuple of (x,y) coords, e.g., ((1,1), (2,3), (4,0))
        
        for block_arrangement in block_permutations:
            # block_arrangement is a tuple of block types, e.g., ('A', 'A', 'C')
            
            total_checks += 1
            if total_checks % 100000 == 0: # Print a status update so we know it's not frozen
                print(f"Checking layout #{total_checks}...")

            # --- Build and Test the Current Layout ---
            
            # a. Build the map of movable blocks for this *specific* loop.
            movable_map_for_this_loop: Dict[Cell, Block] = {}
            for i in range(num_movables):
                spot = spot_combo[i]
                block_type = block_arrangement[i]
                
                # ======================================================
                # --- THIS IS THE OPTIMIZATION ---
                # We are NOT calling Reflect() or Opaque().
                # We're just grabbing the shared object from our "pool".
                movable_map_for_this_loop[spot] = BLOCK_PROTOTYPES[block_type]
                # ======================================================

            # b. Add these movable blocks to our main map.
            #    .update() is fast.
            current_blocks_map.update(movable_map_for_this_loop)

            # c. RUN THE SIMULATION!
            #    This calls your 'trace_all' function to see what happens.
            sim_result = trace_all(grid, lazors, target_set, current_blocks_map, rows, cols)

            #
            # --- *** THIS IS THE BUG FIX *** ---
            #
            # d. Did we win?
            #    We must add a 'safety check' in case tracer.py
            #    failed and returned None.
            if sim_result and sim_result['covered_targets'] == target_set:
            #
            # --- *** END OF BUG FIX *** ---
            #
                print(f"\n--- SOLUTION FOUND! (after {total_checks} checks) ---")
                
                # Found it! Let's return a simple dictionary of the solution.
                solution_layout = {spot_combo[i]: block_arrangement[i] for i in range(num_movables)}
                return solution_layout
            
            # e. Clean up for the next loop.
            #    We have to remove the blocks we just added so the map is
            #    ready for the *next* combination.
            #    (This is faster than making a full .copy() every time).
            for spot in movable_map_for_this_loop:
                del current_blocks_map[spot]
            
            # (If no match, the loop continues to the next layout)

    # If we get all the way here, it means the loops finished and found nothing.
    print(f"\nNo solution found after checking all {total_checks} possible layouts.")
    return None


def format_solution_to_grid(grid: Grid, solution: Dict[Cell, str]) -> List[List[str]]:
    """
    A helper function to create the "easy to understand" output file.
    It just takes the solution layout and plugs it into the original grid.
    """
    # Make a deep copy of the grid so we don't mess up the original
    solution_grid = [row[:] for row in grid]
    
    # Go through our solution and plop the blocks (A, B, C) onto the grid
    for (x, y), block_type in solution.items():
        # Quick check to make sure the coordinates are valid
        if 0 <= y < len(solution_grid) and 0 <= x < len(solution_grid[y]):
            solution_grid[y][x] = block_type # Overwrite the 'o'
    
    return solution_grid

# --- This is where the script actually starts running ---
#
# ========= MODIFICATION START =========
#
# 
# 
# 
#
if __name__ == "__main__":
    
    # Check if the user provided at least one file.
    if len(sys.argv) < 2:
        print("Usage: python solver.py <file1.bff> [file2.bff] [file3.bff] ...")
        print("Tip: You can use a wildcard (glob) to run all files in a folder:")
        print("     python solver.py bff_files/*.bff")
        sys.exit(1)

    # Get the list of all files to solve (everything after 'solver.py')
    bff_paths = sys.argv[1:]
    
    print(f"--- Lazor Solver Batch Mode ---")
    print(f"Found {len(bff_paths)} file(s) to process.")
    
    solved_count = 0
    failed_count = 0
    
    # Loop over every file path provided
    for bff_path in bff_paths:
        print(f"\n=============================================")
        print(f" PROCESSING: {bff_path}")
        print(f"=============================================")
        
        try:
            # 1. Parse the file (using your parser.py)
            grid_data, blocks, lazors_data, targets_data = parse_bff(bff_path)
            
            # --- Start Timer ---
            # (Assignment requires checking performance)
            start_time = time.time()
            
            # 2. Run the solver! (This is the big 'solve' function from above)
            solution = solve(grid_data, blocks, lazors_data, targets_data)
            
            # --- Stop Timer ---
            end_time = time.time()
            duration = end_time - start_time
            
            # 3. Handle the result
            if solution:
                solved_count += 1
                print(f"\n--- SUCCESS: Solution found in {duration:.4f} seconds ---")
                
                print("\nSolution Layout (position: block):")
                print(solution)
                
                print("\nVisualized Solution Grid (matches assignment requirement #3):")
                # Format and print the visual grid
                solved_grid = format_solution_to_grid(grid_data, solution)
                for row in solved_grid:
                    print(" ".join(row))
                
                # --- Write solution to a .txt file ---
                output_filename = f"{bff_path}_solution.txt"
                try:
                    with open(output_filename, "w") as f:
                        for row in solved_grid:
                            f.write(" ".join(row) + "\n")
                        f.write(f"\nSolved in {duration:.4f} seconds.")
                    print(f"\nSolution also written to {output_filename}")
                except Exception as e:
                    print(f"\nWarning: Could not write solution file. Error: {e}")

            else:
                # The solver returned None
                failed_count += 1
                print(f"\n--- FAILURE: No solution found. (Time taken: {duration:.4f}s) ---")

        except FileNotFoundError:
            print(f"\n--- ERROR: File not found ---")
            print(f"Cannot find: {bff_path}")
            print("Please check the file path and try again.")
            failed_count += 1
        except Exception as e:
            print(f"\n--- AN UNEXPECTED ERROR OCCURRED ---")
            print(f"Error details: {e}")
            failed_count += 1

    # --- Print Final Summary ---
    print(f"\n=============================================")
    print(f"         BATCH PROCESSING COMPLETE")
    print(f"=============================================")
    print(f"Total Solved: {solved_count}")
    print(f"Total Failed/Not Found: {failed_count}")
    print(f"=============================================")
