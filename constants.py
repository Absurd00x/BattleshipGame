#
# Window parameters
#

X_TILES = 10
Y_TILES = 10

WIDTH = 50 * X_TILES
HEIGHT = 37 * Y_TILES

STRETCHED_WIDTH = 100 * X_TILES
STRETCHED_HEIGHT = 40 * Y_TILES

FRAME_WIDTH = 300
FRAME_HEIGHT = 400

STRETCHED_FRAME_WIDTH = 600
STRETCHED_FRAME_HEIGHT = 150

NORMAL_FRAME_X_INDENT = 0.69
NORMAL_FRAME_Y_INDENT = 0.45

STRETCHED_FRAME_X_INDENT = 0.6
STRETCHED_FRAME_Y_INDENT = 0.45

CELL_WIDTH = FRAME_WIDTH // X_TILES // 100
CELL_HEIGHT = FRAME_HEIGHT // Y_TILES // 100

STRETCHED_CELL_WIDTH = STRETCHED_FRAME_WIDTH // X_TILES // 10
STRETCHED_CELL_HEIGHT = STRETCHED_FRAME_HEIGHT // Y_TILES // 10

BUTTONS_PER_COLUMN = 5

#
# Button parameters
#

BUTTON_HEIGHT = 3
BUTTON_WIDTH = 6
BUTTON_BORDER = 1
X_INDENT = 0.16
Y_INDENT = 0.19
STRETCHED_X_INDENT = 0.09
STRETCHED_Y_INDENT = 0.18
BUTTON_COLOUR = 'Grey'

#
# Ship parameters
#

SHIP_TYPES = 4
TOTAL_PARTS = SHIP_TYPES * (SHIP_TYPES + 1) * (SHIP_TYPES + 2) / 6  # Shout-out to Ivangelie
HORIZONTAL = 'horizontal'
VERTICAL = 'vertical'
PLAYER_COLOUR = 'Yellow'
HIT_COLOUR = 'Red'
MISS_COLOUR = 'Cyan'

#
# Neural network parameters
#

INPUT_NODES = 14
HIDDEN_NODES = 200
OUTPUT_NODES = 1
LEARNING_RATE = 0.00001

# Number of ways to place the biggest in each cell
# These values are intentionally put in segment [0, 1]
HEURISTIC_CENTER = [[(min(i + 1, X_TILES - i, SHIP_TYPES) +
                     min(j + 1, Y_TILES - j, SHIP_TYPES)) /
                     (10 ** len(str(SHIP_TYPES * 2)))
                     for j in range(Y_TILES)] for i in range(X_TILES)]

# This heuristic should teach NN to shoot in chess-like order. Like this:
# x.x.x.x.x.x
# .x.x.x.x.x.
# x.x.x.x.x.x
HEURISTIC_CHESS = [[0.99 if (i + j) % 2 == 0 else 0.01 for j in range(Y_TILES)] for i in range(X_TILES)]

CONFIDENCE_DELAY = 0.5
TRAINING = False
SHOW_CONFIDENCE = False
FILE_NAME = 'data.txt'

SHIFTS = ((-1, 0), (-1, 1), (0, 1), (1, 1), (1, 0), (1, -1), (0, -1), (-1, -1))
