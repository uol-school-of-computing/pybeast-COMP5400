from typing import List
from numpy.random import rand

# An enumeration type for colours.

class ColourType:
    COLOUR_BLACK = 0
    COLOUR_WHITE = 1
    COLOUR_GREEN = 2
    COLOUR_BLUE = 3
    COLOUR_RED = 4
    COLOUR_PURPLE = 5
    COLOUR_DARK_PURPLE = 6
    COLOUR_YELLOW = 7
    COLOUR_LILAC = 8
    COLOUR_BROWN = 9
    COLOUR_LIGHT_GREY = 10
    COLOUR_DARK_GREY = 11
    COLOUR_MID_GREY = 12
    COLOUR_ORANGE = 13
    COLOUR_PINK = 14
    COLOUR_SELECTION = 15


# A global colour palette. Could probably do with many more colours.
ColourPalette = [
    [0.0, 0.0, 0.0, 1.0],  # black
    [1.0, 1.0, 1.0, 1.0],  # white
    [0.2, 0.8, 0.2, 1.0],  # green
    [0.2, 0.2, 0.8, 1.0],  # blue
    [0.8, 0.2, 0.2, 1.0],  # red
    [0.5, 0.3, 0.7, 1.0],  # purple
    [0.2, 0.0, 0.4, 1.0],  # dark purple
    [0.8, 0.8, 0.2, 1.0],  # yellow
    [0.8, 0.5, 0.9, 1.0],  # lilac
    [0.4, 0.3, 0.1, 1.0],  # brown
    [0.8, 0.8, 0.8, 1.0],  # light grey
    [0.3, 0.3, 0.3, 1.0],  # dark grey
    [0.5, 0.5, 0.5, 1.0],  # mid grey
    [0.9, 0.9, 0.1, 1.0],  # orange
    [1.0, 0.8, 0.8, 1.0],  # np.pink
    [0.5, 0.5, 1.0, 0.5]  # selected
]

# Returns a random colour, all set for input to glColor4fv
def random_colour() -> List[float]:
    colour = rand(4).tolist()
    return colour
