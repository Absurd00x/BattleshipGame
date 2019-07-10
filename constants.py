#
# Главное окно
#

X_TILES = 10
Y_TILES = 10

WIDTH = 75 * X_TILES
HEIGHT = 35 * Y_TILES

STATISTICS_LABEL_X = 0.09
STATISTICS_LABEL_Y = 0.05

SCORE_LABEL_X = 0.025
PLAYER_SCORE_LABEL_Y = 0.15
BOT_SCORE_LABEL_Y = 0.25
WINRATE_LABEL_Y = 0.35
INFO_LABEL_Y = 0.85

#
# Игровое поле
#

PLAYER_GRID_X = 0.425
BOT_GRID_X = 0.8
GRID_Y = 0.45

BELONG_LABEL_Y = 0.9
PLAYER_LABEL_X = 0.3865
BOT_LABEL_X = 0.7375

# Эти параметры надо поменять в grid.py в функции place_cells
CELL_WIDTH = 8
CELL_HEIGHT = 2

#
# Параметры кнопок
#

BUTTON_HEIGHT = 3
BUTTON_WIDTH = 8

BUTTON_FRAME_X = 0.025
BUTTON_FRAME_Y = 0.45

BUTTON_BORDER = 5

BUTTON_COLOUR = 'Grey'

BUTTONS_PER_COLUMN = 2

#
# Параметры корабля
#

SHIP_TYPES = 4
TOTAL_PARTS = SHIP_TYPES * (SHIP_TYPES + 1) * (SHIP_TYPES + 2) / 6  # Shout-out to Ivangelie

HORIZONTAL = 'horizontal'
VERTICAL = 'vertical'

DEFAULT_COLOUR = 'Grey'
SHIP_COLOUR = 'Yellow'
HIT_COLOUR = 'Red'
MISS_COLOUR = 'Cyan'

# Количество способов поместить самый большой корабль, проходя через эту клетку
HEURISTIC_CENTER = [[(min(i + 1, X_TILES - i, SHIP_TYPES) +
                     min(j + 1, Y_TILES - j, SHIP_TYPES))
                     for j in range(Y_TILES)] for i in range(X_TILES)]

# Эта эвристика вводит шахматный порядок. Вот так:
# x.x.x.x.x.x
# .x.x.x.x.x.
# x.x.x.x.x.x
HEURISTIC_CHESS1 = [[((i + j) % 2) * SHIP_TYPES * 2 for j in range(Y_TILES)] for i in range(X_TILES)]
HEURISTIC_CHESS2 = [[((i + j + 1) % 2) * SHIP_TYPES * 2 for j in range(Y_TILES)] for i in range(X_TILES)]

#
# Прочее
#

SOLUTION_DELAY = 0.3
FILE_NAME = 'scores.txt'

SHIFTS_AROUND = ((-1, 0), (-1, 1), (0, 1), (1, 1), (1, 0), (1, -1), (0, -1), (-1, -1))
SHIFTS_DIAGONAL = ((-1, -1), (1, -1), (1, 1), (-1, 1))
SHIFTS_HORIZONTAL_VERTICAL = ((0, 1), (1, 0), (0, -1), (-1, 0))


def tile_exists(x, y):
    return -1 < x < X_TILES and -1 < y < Y_TILES


def apply_shift(x, y, shifts):
    for x_shift, y_shift in shifts:
        x_shifted = x + x_shift
        y_shifted = y + y_shift
        if tile_exists(x_shifted, y_shifted):
            yield x_shifted, y_shifted


if __name__ == '__main__':
    print(*HEURISTIC_CHESS1, sep='\n', end='\n\n')
    print(*HEURISTIC_CHESS2, sep='\n', end='\n\n')
