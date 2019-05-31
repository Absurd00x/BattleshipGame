from numpy import array as numpy_array

#
# Window
#

X_TILES = 10
Y_TILES = 10

WIDTH = 50 * X_TILES
HEIGHT = 37 * Y_TILES

STRETCHED_WIDTH = 100 * X_TILES
STRETCHED_HEIGHT = 40 * Y_TILES

#
# Grid
#

GRID_WIDTH = 300
GRID_HEIGHT = 400

STRETCHED_FRAME_WIDTH = 600
STRETCHED_FRAME_HEIGHT = 150

NORMAL_FRAME_X_INDENT = 0.69
NORMAL_FRAME_Y_INDENT = 0.45

STRETCHED_FRAME_X_INDENT = 0.6
STRETCHED_FRAME_Y_INDENT = 0.45

CELL_WIDTH = GRID_WIDTH // X_TILES // 100
CELL_HEIGHT = GRID_HEIGHT // Y_TILES // 100

STRETCHED_CELL_WIDTH = STRETCHED_FRAME_WIDTH // X_TILES // 10
STRETCHED_CELL_HEIGHT = STRETCHED_FRAME_HEIGHT // Y_TILES // 10

#
# Button parameters
#

BUTTON_FRAME_WIDTH = 225
BUTTON_FRAME_HEIGHT = 350

BUTTON_HEIGHT = 3
BUTTON_WIDTH = 6

BUTTON_BORDER = 5

X_INDENT = 0.16
Y_INDENT = 0.19

STRETCHED_X_INDENT = 0.09
STRETCHED_Y_INDENT = 0.18

BUTTON_COLOUR = 'Grey'

BUTTONS_PER_COLUMN = 5

#
# Ship parameters
#

SHIP_TYPES = 4
TOTAL_PARTS = SHIP_TYPES * (SHIP_TYPES + 1) * (SHIP_TYPES + 2) / 6  # Shout-out to Ivangelie

HORIZONTAL = 'horizontal'
VERTICAL = 'vertical'

DEFAULT_COLOUR = 'Grey'
PLAYER_COLOUR = 'Yellow'
HIT_COLOUR = 'Red'
MISS_COLOUR = 'Cyan'

# Number of ways to place the biggest in each cell
# These values are intentionally put in segment [0, 1]
HEURISTIC_CENTER = [[(min(i + 1, X_TILES - i, SHIP_TYPES) +
                     min(j + 1, Y_TILES - j, SHIP_TYPES))
                     for j in range(Y_TILES)] for i in range(X_TILES)]

# This heuristic implements chess-like order. Like this:
# x.x.x.x.x.x
# .x.x.x.x.x.
# x.x.x.x.x.x
HEURISTIC_CHESS1 = numpy_array([[((i + j) % 2) * SHIP_TYPES * 2 for j in range(Y_TILES)] for i in range(X_TILES)])
HEURISTIC_CHESS2 = numpy_array([[((i + j + 1) % 2) * SHIP_TYPES * 2 for j in range(Y_TILES)] for i in range(X_TILES)])

HEURISTIC_SUMMARY = numpy_array([[HEURISTIC_CENTER[i][j] + HEURISTIC_CHESS1[i][j]
                                for j in range(Y_TILES)]
                                for i in range(X_TILES)])

GAMES_TO_AUTOSAVE = 100
SOLVING = False
SOLUTION = False
SOLUTION_DELAY = 0.3
MAXIMUM_GAMES = 200000
FILE_NAME = 'data.txt'

SHIFTS_AROUND = ((-1, 0), (-1, 1), (0, 1), (1, 1), (1, 0), (1, -1), (0, -1), (-1, -1))
SHIFTS_DIAGONAL = ((-1, -1), (1, -1), (1, 1), (-1, 1))
SHIFTS_HORIZONTAL_VERTICAL = ((0, 1), (1, 0), (0, -1), (-1, 0))

if __name__ == '__main__':
    print(*HEURISTIC_CHESS1, sep='\n', end='\n\n')
    print(*HEURISTIC_CHESS2, sep='\n', end='\n\n')
