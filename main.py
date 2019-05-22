# TODO:
#  1) Neural network does not learn shit.
#  2) I definitely should implement genetic selection algorithm
#  because there is nothing that punishes neural network for
#  solving the grid in maximum possible amount of turns.

import tkinter as tk
import shelve
import neuralnetwork
from random import randint
from time import sleep

# Window parameters

X_TILES = 10
Y_TILES = 10
WIDTH = 50 * X_TILES
HEIGHT = 35 * Y_TILES
FRAME_WIDTH = 300
FRAME_HEIGHT = 400
CELL_WIDTH = FRAME_WIDTH // X_TILES // 100
CELL_HEIGHT = FRAME_HEIGHT // Y_TILES // 100
BUTTONS_PER_COLUMN = 5

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
PLAYER_COLOUR = 'Yellow'

# Neural network parameters

INPUT_NODES = 8
HIDDEN_NODES = 100
OUTPUT_NODES = 1
LEARNING_RATE = 0.00003
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


class FitError(Exception):
    """
    An exception in case the program was unable to place all ships
    """
    def __init__(self):
        super().__init__('Could not fit all the ships into battlefield')


class Fleet:
    def __init__(self):
        self.ships = []
        self.colour = PLAYER_COLOUR
        self.taken = [[False for _ in range(Y_TILES)] for _ in range(X_TILES)]
        for number in range(1, SHIP_TYPES + 1):
            self.place_ship(SHIP_TYPES - number + 1, number)
        self.parts_alive = TOTAL_PARTS

    def check_tiles_around(self, x, y):
        for x_shift, y_shift in SHIFTS:
            shifted_x = x + x_shift
            shifted_y = y + y_shift
            if tile_exists(shifted_x, shifted_y):
                if self.taken[x + x_shift][y + y_shift]:
                    return True
        return False

    def place_ship(self, size, to_place):

        placed = 0
        tries = 100
        current_try = 0

        while placed < to_place:
            if current_try == tries:
                raise FitError
            replace = False
            x_pos, y_pos = None, None
            rotation = HORIZONTAL if randint(0, 1) else VERTICAL
            if rotation is HORIZONTAL:
                x_pos = randint(0, X_TILES - 1)
                y_pos = randint(0, Y_TILES - size)

                # Сначала проверяем - не задеваем ли мы другой корабль такой постановкой
                for y in range(y_pos, y_pos + size):
                    replace = (self.check_tiles_around(x_pos, y)
                               or self.taken[x_pos][y])
                    if replace:
                        break
                if not replace:
                    for y in range(y_pos, y_pos + size):
                        self.taken[x_pos][y] = True

            elif rotation is VERTICAL:
                x_pos = randint(0, X_TILES - size)
                y_pos = randint(0, Y_TILES - 1)

                # Проверка
                for x in range(x_pos, x_pos + size):
                    replace = (self.check_tiles_around(x, y_pos)
                               or self.taken[x][y_pos])
                    if replace:
                        break
                if not replace:
                    for x in range(x_pos, x_pos + size):
                        self.taken[x][y_pos] = True

            current_try += 1

            if not replace:
                self.ships.append(Ship(x_pos, y_pos, size, rotation))
                placed += 1
                current_try = 0

#
# Сетка
#


def tile_exists(x, y):
    return -1 < x < X_TILES and -1 < y < Y_TILES


class Grid:
    def __init__(self):
        self.cells = [[tk.Button(master=frame, bg='Grey', bd=1, width=CELL_WIDTH, height=CELL_HEIGHT)
                       for _ in range(Y_TILES)] for _ in range(X_TILES)]

        for x in range(X_TILES):
            for y in range(Y_TILES):
                self.cells[x][y].config(command=lambda i=x, j=y: self.click_logic(i, j))
                self.cells[x][y].grid(row=x, column=y)

        self.player = Fleet()

    def hide(self):
        for ship in self.player.ships:
            if ship.rotation is HORIZONTAL:
                for y_pos in range(ship.y, ship.y + ship.size):
                    if self.cells[ship.x][y_pos]['bg'] != 'Red':
                        self.cells[ship.x][y_pos]['bg'] = 'Grey'
            elif ship.rotation is VERTICAL:
                for x_pos in range(ship.x, ship.x + ship.size):
                    if self.cells[x_pos][ship.y]['bg'] != 'Red':
                        self.cells[x_pos][ship.y]['bg'] = 'Grey'

    def reveal(self):
        for ship in self.player.ships:
            if ship.rotation is HORIZONTAL:
                for y_pos in range(ship.y, ship.y + ship.size):
                    if self.cells[ship.x][y_pos]['bg'] == 'Grey':
                        self.cells[ship.x][y_pos]['bg'] = PLAYER_COLOUR
            elif ship.rotation is VERTICAL:
                for x_pos in range(ship.x, ship.x + ship.size):
                    if self.cells[x_pos][ship.y]['bg'] == 'Grey':
                        self.cells[x_pos][ship.y]['bg'] = PLAYER_COLOUR

    def click_logic(self, i, j):
        if self.player.taken[i][j]:
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
        # Stupid tkinter objects need to be destroyed manually
        for cell_row in self.cells:
            for cell in cell_row:
                cell.destroy()
        self.__init__()

# Логика нейронки


def create_new_neural_network():
    file = shelve.open('weights')
    nn = neuralnetwork.NeuralNetwork(INPUT_NODES, HIDDEN_NODES, OUTPUT_NODES, LEARNING_RATE)
    file['nn'] = nn
    file.close()


def train_neural_network():
    board = 0
    while board < BOARDS_TO_SOLVE:
        solve_with_neural_network()
        battlefield.refresh()
        root.update()
        board += 1


def solve_with_neural_network():
    # Достаем нейронку из файла
    with shelve.open('weights') as file:
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
        while battlefield.player.parts_alive > 0:
            nn_input = None
            nn_answer = (None, None)
            maximum_confidence = 0
            for i in range(X_TILES):
                for j in range(Y_TILES):
                    if battlefield.cells[i][j]['bg'] == 'Grey':
                        # Ищем корабли вокруг клетки
                        ships = []
                        #inactive_cells = []
                        for i_shift, j_shift in SHIFTS:
                            shifted_i = i + i_shift
                            shifted_j = j + j_shift
                            if not tile_exists(shifted_i, shifted_j):
                                ships.append(0.01)
                                #inactive_cells.append(0.99)
                            else:
                                if battlefield.cells[shifted_i][shifted_j]['bg'] == 'Red':
                                    ships.append(0.99)
                                else:
                                    ships.append(0.01)
                                #if battlefield.cells[shifted_i][shifted_j]['state'] == 'disabled':
                                #    inactive_cells.append(0.99)
                                #else:
                                #    inactive_cells.append(0.01)

                        # Расстояния до границ экрана
                        """
                        border_dist = [i, j, X_TILES - i - 1, Y_TILES - j - 1]
    
                        # Расстояния до ближайшего подбитого корабля
    
                        ships_dist = []
    
                        # Если мы не найдем корабль, то будем считать, что он находится за полем
    
                        dist = 10
                        for x in range(i + 1, X_TILES):
                            if battlefield.cells[x][j]['bg'] == 'Red':
                                dist = x - i - 1
                                break
                        ships_dist.append(dist / 10)
                        dist = 10
                        for x in range(i - 1, -1, -1):
                            if battlefield.cells[x][j]['bg'] == 'Red':
                                dist = i - x - 1
                                break
                        ships_dist.append(dist / 10)
                        dist = 10
                        for y in range(j + 1, Y_TILES):
                            if battlefield.cells[i][y]['bg'] == 'Red':
                                dist = y - j - 1
                                break
                        ships_dist.append(dist / 10)
                        dist = 10
                        for y in range(j - 1, -1, -1):
                            if battlefield.cells[i][y]['bg'] == 'Red':
                                dist = j - y - 1
                                break
                        ships_dist.append(dist / 10)
    
                        # Аналогично считаем расстояние до ближайшей неактивной клетки
    
                        inactive_dist = []
                        dist = 10
                        for x in range(i + 1, X_TILES):
                            if battlefield.cells[x][j]['state'] == 'disabled':
                                dist = x - i - 1
                                break
                        inactive_dist.append(dist / 10)
                        dist = 10
                        for x in range(i - 1, -1, -1):
                            if battlefield.cells[x][j]['state'] == 'disabled':
                                dist = i - x - 1
                                break
                        inactive_dist.append(dist / 10)
                        dist = 10
                        for y in range(j + 1, Y_TILES):
                            if battlefield.cells[i][y]['state'] == 'disabled':
                                dist = y - j - 1
                                break
                        inactive_dist.append(dist / 10)
                        dist = 10
                        for y in range(j - 1, -1, -1):
                            if battlefield.cells[i][y]['state'] == 'disabled':
                                dist = j - y - 1
                                break
                        inactive_dist.append(dist / 10)
                        """
                        # Сливаем все это добро в один массив - это и есть вход для нейронки

                        nn_input = ships# + inactive_cells + ships_dist + inactive_dist + border_dist
                        confidence = nn.query(nn_input)
                        if confidence > maximum_confidence:
                            nn_answer = (i, j)
                            maximum_confidence = confidence
                        battlefield.cells[i][j]['bg'] = 'Grey'
                        root.update()
            battlefield.click_logic(nn_answer[0], nn_answer[1])
            correct_answer = [1] if battlefield.cells[nn_answer[0]][nn_answer[1]]['bg'] == 'Red' else [0]
            nn.train(nn_input, correct_answer)
            sleep(DELAY)
        file['nn'] = nn


root = tk.Tk()
root.geometry('{}x{}'.format(WIDTH, HEIGHT))

frame = tk.Frame(root, width=FRAME_WIDTH, height=FRAME_HEIGHT)
frame.place(relx=0.69, rely=0.5, anchor='center')

battlefield = Grid()

UI_buttons = {'hide': tk.Button(text='Hide', command=battlefield.hide),
              'reveal': tk.Button(text='Reveal', command=battlefield.reveal),
              'refresh': tk.Button(text='Refresh', command=battlefield.refresh),
              'solve': tk.Button(text='Solve', command=solve_with_neural_network),
              'train': tk.Button(text='Train', command=train_neural_network),
              'new': tk.Button(text='Recreate\nNN', command=create_new_neural_network),
              'exit': tk.Button(text='Exit', command=root.destroy)}

for UI_button in UI_buttons.values():
    UI_button.config(bg=BUTTON_COLOUR, width=BUTTON_WIDTH, height=BUTTON_HEIGHT, bd=BUTTON_BORDER)

buttons_matrix = [list(UI_buttons.values())[i:i+BUTTONS_PER_COLUMN]
                  for i in range(0, len(UI_buttons), BUTTONS_PER_COLUMN)]

for column_index in range(len(buttons_matrix)):
    for row_index in range(len(buttons_matrix[column_index])):
        buttons_matrix[column_index][row_index].place(relx=(0.02 + 0.16 * column_index), rely=(0.025 + 0.19 * row_index))

tk.mainloop()
