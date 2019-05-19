# TODO:
#  1) Neural network does not learn shit.
#  2) There is a memory leak somewhere because after.
#  like 10000 board this script takes the whole CPU core memory
#  3) I definitely should implement genetic selection algorithm
#  because there is nothing that punishes neural network for
#  solving the grid in maximum possible amount of turns.

import tkinter as tk
import shelve
import neuralnetwork
from random import randint
from time import sleep

# Field parameters

X_TILES = 10
Y_TILES = 10
WIDTH = 45 * X_TILES
HEIGHT = 35 * Y_TILES
FRAME_WIDTH = 300
FRAME_HEIGHT = 400
CELL_WIDTH = FRAME_WIDTH // X_TILES // 100
CELL_HEIGHT = FRAME_HEIGHT // Y_TILES // 100

# Button parameters

BUTTON_COLOUR = 'Grey'
BUTTON_HEIGHT = 3
BUTTON_WIDTH = 6
BUTTON_BORDER = 1

# Ship parameters

SHIP_TYPES = 4
TOTAL_PARTS = SHIP_TYPES * (SHIP_TYPES + 1) * (SHIP_TYPES + 2) / 6  # Shout-out to Ivangelie
HORIZONTAL = 'horizontal'
VERTICAL = 'vertical'

# Neural network parameters

INPUT_NODES = 28
HIDDEN_NODES = 20
OUTPUT_NODES = 1
LEARNING_RATE = 0.7
DELAY = 0  # 0.0625
BOARDS_TO_SOLVE = 100

SHIFTS = ((-1, 0), (-1, 1), (0, 1), (1, 1), (1, 0), (1, -1), (0, -1), (-1, -1))

#
# Корабль
#


class Ship:
    def __init__(self, x, y, size, rotation):
        self.x = x
        self.y = y
        self.size = size
        self.rotation = rotation

#
# Флот
#


class Fleet:
    def __init__(self, grid, colour):
        self.grid = grid
        self.ships = []
        self.colour = colour
        for number in range(1, SHIP_TYPES + 1):
            self.place_ship(SHIP_TYPES - number + 1, number)
        self.parts_alive = TOTAL_PARTS

    def place_ship(self, size, to_place):

        placed = 0

        while placed < to_place:
            replace = False
            x_pos, y_pos = None, None
            rotation = HORIZONTAL if randint(0, 1) else VERTICAL
            if rotation is HORIZONTAL:
                x_pos = randint(0, X_TILES - 1)
                y_pos = randint(0, Y_TILES - size)

                # Сначала проверяем - не задеваем ли мы другой корабль такой постановкой
                for y in range(y_pos, y_pos + size):
                    replace = (self.grid.check_tiles_around(x_pos, y)
                               or self.grid.taken[x_pos][y])
                    if replace:
                        break
                if not replace:
                    for y in range(y_pos, y_pos + size):
                        self.grid.taken[x_pos][y] = True

            elif rotation is VERTICAL:
                x_pos = randint(0, X_TILES - size)
                y_pos = randint(0, Y_TILES - 1)

                # Проверка
                for x in range(x_pos, x_pos + size):
                    replace = (self.grid.check_tiles_around(x, y_pos)
                               or self.grid.taken[x][y_pos])
                    if replace:
                        break
                if not replace:
                    for x in range(x_pos, x_pos + size):
                        self.grid.taken[x][y_pos] = True

            if not replace:
                self.ships.append(Ship(x_pos, y_pos, size, rotation))
                root.update()
                placed += 1

    def hide(self):
        for ship in self.ships:
            if ship.rotation is HORIZONTAL:
                for y_pos in range(ship.y, ship.y + ship.size):
                    if self.grid.cells[ship.x][y_pos]['bg'] != 'Red':
                        self.grid.cells[ship.x][y_pos]['bg'] = 'Grey'
            elif ship.rotation is VERTICAL:
                for x_pos in range(ship.x, ship.x + ship.size):
                    if self.grid.cells[x_pos][ship.y]['bg'] != 'Red':
                        self.grid.cells[x_pos][ship.y]['bg'] = 'Grey'

    def reveal(self):
        for ship in self.ships:
            if ship.rotation is HORIZONTAL:
                for y_pos in range(ship.y, ship.y + ship.size):
                    if self.grid.cells[ship.x][y_pos]['bg'] == 'Grey':
                        self.grid.cells[ship.x][y_pos]['bg'] = self.colour
            elif ship.rotation is VERTICAL:
                for x_pos in range(ship.x, ship.x + ship.size):
                    if self.grid.cells[x_pos][ship.y]['bg'] == 'Grey':
                        self.grid.cells[x_pos][ship.y]['bg'] = self.colour

#
# Сетка
#


def tile_exists(x, y):
    return -1 < x < X_TILES and -1 < y < Y_TILES


class Grid:
    def __init__(self, frame, player_colour):
        self.frame = frame
        self.cells = [[tk.Button(master=frame, bg='Grey', bd=1, width=CELL_WIDTH, height=CELL_HEIGHT)
                       for _ in range(Y_TILES)] for _ in range(X_TILES)]

        self.taken = [[False for _ in range(Y_TILES)] for _ in range(X_TILES)]

        for x in range(X_TILES):
            for y in range(Y_TILES):
                self.cells[x][y].config(command=lambda i=x, j=y: self.click_logic(i, j))
                self.cells[x][y].grid(row=x, column=y)
        self.player = Fleet(self, player_colour)

    def check_tiles_around(self, x, y):
        for x_shift, y_shift in SHIFTS:
            shifted_x = x + x_shift
            shifted_y = y + y_shift
            if tile_exists(shifted_x, shifted_y):
                if self.taken[x + x_shift][y + y_shift]:
                    return True
        return False

    def click_logic(self, i, j):
        if self.taken[i][j]:
            self.cells[i][j]['bg'] = 'Red'
            self.player.parts_alive -= 1
            # Логика по которой нельзя кликать на клетки, на которых
            # в принципе не может быть корабля
            # single = not self.check_tiles_around(i, j)
            # if single:
            #     for i_shift, j_shift in SHIFTS:
            #         shifted_i = i + i_shift
            #         shifted_j = j + j_shift
            #         if tile_exists(shifted_i, shifted_j):
            #             self.cells[shifted_i][shifted_j].config(bg='Cyan', state='disabled')
        else:
            self.cells[i][j]['bg'] = 'Cyan'
        self.cells[i][j]['state'] = 'disabled'

    def refresh(self):
        self.__init__(self.frame, self.player.colour)

# Логика нейронки


def create_new_neural_network():
    file = shelve.open('weights')
    nn = neuralnetwork.NeuralNetwork(INPUT_NODES, HIDDEN_NODES, OUTPUT_NODES, LEARNING_RATE)
    file['nn'] = nn
    file.close()


def train_neural_network(field):
    board = 0
    while board < BOARDS_TO_SOLVE:
        solve_with_neural_network(field)
        field.refresh()
        board += 1


def solve_with_neural_network(field):
    # Достаем нейронку из файла
    file = shelve.open('weights')
    nn = file['nn']
    """
    Формируем вход для нейронки я ей показываю:
    Подбитые корабли вокруг клетки
    Неактивные клетки вокруг клетки
    Расстояния до ближайшего подбитого корабля
    Расстояния до ближайших неактивных клеток
    Расстояния до границ экрана
    Нейронка отдельно обрабатывает каждую клетку
    """
    while field.player.parts_alive > 0:
        nn_input = None
        nn_answer = (None, None)
        maximum_confidence = 0
        for i in range(X_TILES):
            for j in range(Y_TILES):
                if field.cells[i][j]['bg'] == 'Grey':

                    # Ищем корабли вокруг клетки

                    ships = []
                    inactive_cells = []
                    for i_shift, j_shift in SHIFTS:
                        shifted_i = i + i_shift
                        shifted_j = j + j_shift
                        if not tile_exists(shifted_i, shifted_j):
                            ships.append(0)
                            inactive_cells.append(1)
                        else:
                            if field.cells[i][j]['bg'] == 'Red':
                                ships.append(1)
                            else:
                                ships.append(0)
                            if field.cells[i][j]['state'] == 'disabled':
                                inactive_cells.append(1)
                            else:
                                inactive_cells.append(0)

                    # Расстояния до границ экрана

                    border_dist = [i, j, X_TILES - i - 1, Y_TILES - j - 1]

                    # Расстояния до ближайшего подбитого корабля

                    ships_dist = []

                    # Если мы не найдем корабль, то будем считать, что он очень далеко

                    dist = 100
                    for x in range(i + 1, X_TILES):
                        if field.cells[x][j]['bg'] == 'Red':
                            dist = x - i - 1
                            break
                    ships_dist.append(dist)
                    dist = 100
                    for x in range(i - 1, -1, -1):
                        if field.cells[x][j]['bg'] == 'Red':
                            dist = i - x - 1
                            break
                    ships_dist.append(dist)
                    dist = 100
                    for y in range(j + 1, Y_TILES):
                        if field.cells[i][y]['bg'] == 'Red':
                            dist = y - j - 1
                            break
                    ships_dist.append(dist)
                    dist = 100
                    for y in range(j - 1, -1, -1):
                        if field.cells[i][y]['bg'] == 'Red':
                            dist = j - y - 1
                            break
                    ships_dist.append(dist)

                    # Аналогично считаем расстояние до ближайшей неактивной клетки

                    inactive_dist = []
                    dist = 100
                    for x in range(i + 1, X_TILES):
                        if field.cells[x][j]['state'] == 'disabled':
                            dist = x - i - 1
                            break
                    inactive_dist.append(dist)
                    dist = 100
                    for x in range(i - 1, -1, -1):
                        if field.cells[x][j]['state'] == 'disabled':
                            dist = i - x - 1
                            break
                    inactive_dist.append(dist)
                    dist = 100
                    for y in range(j + 1, Y_TILES):
                        if field.cells[i][y]['state'] == 'disabled':
                            dist = y - j - 1
                            break
                    inactive_dist.append(dist)
                    dist = 100
                    for y in range(j - 1, -1, -1):
                        if field.cells[i][y]['state'] == 'disabled':
                            dist = j - y - 1
                            break
                    inactive_dist.append(dist)

                    # Сливаем все это добро в один массив - это и есть вход для нейронки

                    nn_input = ships + inactive_cells + ships_dist + inactive_dist + border_dist
                    confidence = nn.query(nn_input)
                    if confidence > maximum_confidence:
                        nn_answer = (i, j)
                        maximum_confidence = confidence
        field.click_logic(nn_answer[0], nn_answer[1])
        correct_answer = [1] if field.cells[nn_answer[0]][nn_answer[1]]['bg'] == 'Red' else [0]
        nn.train(nn_input, correct_answer)
        sleep(DELAY)
        root.update()
    file['nn'] = nn
    file.close()


root = tk.Tk()
root.geometry('{}x{}'.format(WIDTH, HEIGHT))

fr = tk.Frame(root, width=FRAME_WIDTH, height=FRAME_HEIGHT)
fr.place(relx=0.6, rely=0.5, anchor='center')

battlefield = Grid(fr, 'yellow')

UI_buttons = {'hide': tk.Button(text='Hide', command=lambda field=battlefield: field.player.hide()),
              'reveal': tk.Button(text='Reveal', command=lambda field=battlefield: field.player.reveal()),
              'refresh': tk.Button(text='Refresh', command=lambda field=battlefield: field.refresh()),
              'solve': tk.Button(text='Solve', command=lambda field=battlefield: solve_with_neural_network(field)),
              'train': tk.Button(text='Train', command=lambda field=battlefield: train_neural_network(field))}

for button in UI_buttons.values():
    button.config(bg=BUTTON_COLOUR, width=BUTTON_WIDTH, height=BUTTON_HEIGHT, bd=BUTTON_BORDER)

for button, indent in zip(UI_buttons.values(), range(len(UI_buttons))):
    button.place(relx=0.05, rely=0.025 + 0.19 * indent)

tk.mainloop()
