"""
blocks.py
Defines behavior of block types for Lazor game:
A = Reflect, B = Opaque, C = Refract.

interact(direction) -> list of outgoing directions
direction is (dx, dy)
"""

class Block:
    """
    Block class: all blocks in laszor game
    """
    def interact(self, direction):
        raise NotImplementedError


def get_hit_side(lazor_pos, lazor_dir, block_pos, block_size=1):
    """
    Identify the specific face of a block that a lazor hits
    - lazor_pos: Coordinates before the lazor hits (x, y)
    - lazor_dir: (dx, dy)
    - block_pos: (x, y)
    return hit_side: hit face (up=top, down=bottom, right/left=right/left)
    """
    x_lazor, y_lazor = lazor_pos
    dx, dy = lazor_dir
    x_block, y_block = block_pos
    block_right = x_block + block_size  # Right side of the block
    block_bottom = y_block + block_size  # Bottom of the block

    # Match hit side according to lazor direction and position
    if dx == 1 and x_lazor == x_block:  # Lazor to the right, hit the left side of the block
        return 'left'
    elif dx == -1 and x_lazor == block_right:  # Lazor to the left, hit the right side of the block
        return 'right'
    elif dy == 1 and y_lazor == y_block:  # Lazor to the down, hit the top of the block
        return 'up'
    elif dy == -1 and y_lazor == block_bottom:  # Lazor to the up, hit the bottom of the block
        return 'down'
    else:
        raise ValueError(
            f"Lazor position{lazor_pos}and direction{lazor_dir}cannot match block position{block_pos}, so the hit side is not confirmed."
        )
    

class Reflect(Block):
    """
    Reflect(A): reverses lazor direction
    """
    def interact(self, direction, hit_side=None):
        dx, dy = direction
        valid_sides = ['up', 'down', 'left', 'right']
        
         # Verfiy the validity of the hit side
        if hit_side not in valid_sides:
            raise ValueError(f"Unvalid hit face'{hit_side}'，only support{valid_sides}")

        # Reverse the corresponding direction according to the type of hit face
        if hit_side in ['up', 'down']:
            # Collision with horizional surface (top/bottom):vertical direction reverses, horizontal direction remains unchanged
            return [(dx, -dy)]
        elif hit_side in ['left', 'right']:
            # Collision with vertical surface (right/left):vertical direction remains unchanged, horizontal direction reverses
            return [(-dx, dy)]
        
        # Fallback: if unexpected direction, reverse
        return [(-dx, -dy)]

    def __repr__(self):
        return "A"


class Opaque(Block):
    """
    Opaque(B): absorbs lazor without output
    """
    def interact(self, direction):
        return []

    def __repr__(self):
        return "B"


class Refract(Block):
    """
    Refract(C): produces 2 beams: reflect + transmitted
    """
    def interact(self, direction):
        dx, dy = direction
        
        # transmitted beam
        transmitted = (dx, dy)

        # reflected beam
        reflected = Reflect().interact(direction)[0]

        # return both beams
        return [transmitted, reflected]

    def __repr__(self):
        return "C"


class FixedBlock(Block):
    """
    Fixed block on .bff file grid
    """
    def __init__(self, block):
        self.block = block

    def interact(self, direction):
        if self.block == 'A':
            return Reflect().interact(direction)
        elif self.block == 'B':
            return Opaque().interact(direction)
        elif self.block == 'C':
            return Refract().interact(direction)
        else:
            raise ValueError("Invalid fixed block type")

    def __repr__(self):
        return f"Fixed({self.block})"
