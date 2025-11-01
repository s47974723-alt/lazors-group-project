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


class Reflect(Block):
    """
    Reflect(A): reverses lazor direction
    """
    def interact(self, direction):
        dx, dy = direction
        return [(-dx, -dy)]

    def __repr__(self):
        return "A"


class Opaque(Block):
    """
    Opaque(B): absorbs laser without output
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
        return [(dx, dy), (-dx, -dy)]

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

