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
from matplotlib import pyplot as plt

# Window parameters

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

# Button parameters

BUTTON_HEIGHT = 3
BUTTON_WIDTH = 6
BUTTON_BORDER = 1
X_INDENT = 0.16
Y_INDENT = 0.19
STRETCHED_X_INDENT = 0.09
STRETCHED_Y_INDENT = 0.18
BUTTON_COLOUR = 'Grey'

# Ship parameters

SHIP_TYPES = 4
TOTAL_PARTS = SHIP_TYPES * (SHIP_TYPES + 1) * (SHIP_TYPES + 2) / 6  # Shout-out to Ivangelie
HORIZONTAL = 'horizontal'
VERTICAL = 'vertical'
PLAYER_COLOUR = 'Yellow'
HIT_COLOUR = 'Red'
MISS_COLOUR = 'Cyan'

# Neural network parameters

INPUT_NODES = 10
HIDDEN_NODES = 100
OUTPUT_NODES = 1
LEARNING_RATE = 0.00001

# Number of ways to place the biggest in each cell
# These values are intentionally put in segment [0, 1]
HEURISTIC_CENTER = [[(min(i + 1, X_TILES - i, SHIP_TYPES) +
                     min(j + 1, Y_TILES - j, SHIP_TYPES)) /
                     (10 ** len(str(SHIP_TYPES * 2)))
                     for j in range(Y_TILES)] for i in range(X_TILES)]
# This heuristic should teach NN to shoot in chess-like order. It's like this:
# x.x.x.x.x.x
# .x.x.x.x.x.
# x.x.x.x.x.x
HEURISTIC_CHESS = [[0.99 if (i + j) % 2 == 0 else 0.01 for j in range(Y_TILES)] for i in range(X_TILES)]

ENTERTAIN_DELAY = 0  # 0.0625
CONFIDENCE_DELAY = 0  # 0.5
TRAINING = False
ENTERTAIN = False
SHOW_CONFIDENCE = False
FILE_NAME = 'data.txt'

SHIFTS = ((-1, 0), (-1, 1), (0, 1), (1, 1), (1, 0), (1, -1), (0, -1), (-1, -1))

#
# Ship
#


class Ship:
    def __init__(self, x, y, size, rotation):
        self.x = x
        self.y = y
        self.size = size
        self.rotation = rotation

#
# Fleet
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
        self.shown = False

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
# Grid
#


def tile_exists(x, y):
    return -1 < x < X_TILES and -1 < y < Y_TILES


class Grid:
    def __init__(self):
        # TODO:
        #  frame is misplaced on refresh
        self.frame = tk.Frame(width=FRAME_WIDTH, height=FRAME_HEIGHT)
        self.cells = [[tk.Button(master=self.frame, bg='Grey', bd=1, width=CELL_WIDTH, height=CELL_HEIGHT)
                       for _ in range(Y_TILES)] for _ in range(X_TILES)]

        for x in range(X_TILES):
            for y in range(Y_TILES):
                self.cells[x][y].config(command=lambda i=x, j=y: self.click_logic(i, j))
                self.cells[x][y].grid(row=x, column=y)

        self.player = Fleet()

    def resize_cells(self, width, height):
        for x in range(X_TILES):
            for y in range(Y_TILES):
                self.cells[x][y].config(width=width, height=height)
                self.cells[x][y].grid(row=x, column=y)

    def show_player(self):
        if self.player.shown:
            self.hide()
            self.player.shown = False
        else:
            self.reveal()
            self.player.shown = True

    def hide(self):
        for ship in self.player.ships:
            if ship.rotation is HORIZONTAL:
                for y_pos in range(ship.y, ship.y + ship.size):
                    if self.cells[ship.x][y_pos]['bg'] != HIT_COLOUR:
                        self.cells[ship.x][y_pos]['bg'] = 'Grey'
            elif ship.rotation is VERTICAL:
                for x_pos in range(ship.x, ship.x + ship.size):
                    if self.cells[x_pos][ship.y]['bg'] != HIT_COLOUR:
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
            self.cells[i][j]['bg'] = HIT_COLOUR
            self.player.parts_alive -= 1
        else:
            self.cells[i][j]['bg'] = MISS_COLOUR
        self.cells[i][j]['state'] = 'disabled'

    def refresh(self):
        # Stupid tkinter objects need to be destroyed manually
        for cell_row in self.cells:
            for cell in cell_row:
                cell.destroy()
        self.__init__()

#
# Smart list
#


class CompressedList:
    def __init__(self, power=10, max_size=100):
        """
        Contains means of added values as their number exceed 'power'.
        Means are stored in 'stored' variable.
        Last added values are stored in 'buff'
        'stored' is resized when it's length exceeds 'max_size'
        """
        self.stored = []
        self.buff = []
        self.power = power
        self.max_size = max_size

    def add(self, new):
        self.buff.append(new)
        if len(self.buff) == self.power:
            # Adding to 'stored'
            self.stored.append((sum(self.buff) / self.power))
            self.buff.clear()
            if len(self.stored) == self.max_size:
                # Resizing 'stored'
                # Every 10 values are compressed in 1
                self.stored = [sum(self[i:i+10]) / 10 for i in range(0, len(self.stored), 10)]
                self.power *= 10

#
# GUI
#


class MyGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root_geometry(WIDTH, HEIGHT)
        self.battlefield = Grid()
        self.battlefield.frame.place(relx=NORMAL_FRAME_X_INDENT, rely=NORMAL_FRAME_Y_INDENT, anchor='center')

        with shelve.open('data.txt') as file:
            self.neural_network = file['nn']
            self.boards_solved = file['solved']
            # Number of misses for each game
            self.neural_network_results = file['results']

        self.solved_label = tk.Label(text='Boards solved: {}'.format(self.boards_solved))
        self.UI_buttons = {'stop': tk.Button(text='Stop\ntraining', command=stop_training),
                           'refresh': tk.Button(text='Refresh\nboard', command=self.battlefield.refresh),
                           'hide': tk.Button(text='Show\nfleet', command=self.battlefield.show_player),
                           'confidence': tk.Button(text='Show\nconfidence', command=self.show_confidence),
                           'recreate': tk.Button(text='Recreate\nNN', command=self.create_new_neural_network),
                           'train': tk.Button(text='Train\nNN', command=self.train_neural_network),
                           'solve': tk.Button(text='Solve\nboard', command=self.solve_with_neural_network),
                           'results': tk.Button(text='Show\nresults', command=self.show_results),
                           'show': tk.Button(text='Show\nsolution', command=show_solution),
                           'exit': tk.Button(text='Exit', command=self.root.destroy)}

        self.buttons_matrix = [list(self.UI_buttons.values())[i:i + BUTTONS_PER_COLUMN]
                               for i in range(0, len(self.UI_buttons), BUTTONS_PER_COLUMN)]

        self.config_buttons(BUTTON_WIDTH, BUTTON_HEIGHT, BUTTON_BORDER, BUTTON_COLOUR)

        self.place_buttons(X_INDENT, Y_INDENT)

        self.solved_label.place(relx=0.6, rely=0.9)

    def root_geometry(self, width, height):
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = int((screen_width / 2) - (width / 2))
        y = int((screen_height / 2) - (height / 2))
        self.root.geometry('{:d}x{:d}+{:d}+{:d}'.format(width, height, x, y))

    def place_buttons(self, x_indent, y_indent):
        for column_index in range(len(self.buttons_matrix)):
            for row_index in range(len(self.buttons_matrix[column_index])):
                self.buttons_matrix[column_index][row_index].place(relx=(0.02 + x_indent * column_index),
                                                                   rely=(0.03 + y_indent * row_index))

    def config_buttons(self, width, height, border, colour):
        for UI_button in self.UI_buttons.values():
            UI_button.config(width=width, height=height, bd=border, bg=colour)

    def show_results(self):
        results = (self.neural_network_results.stored if len(self.neural_network_results.stored) else
                   self.neural_network_results.buff)
        games_played = [n for n in range(1, len(results) + 1)]
        plt.plot(games_played, results)
        plt.title('Game history')
        plt.xlabel('Games played')
        plt.ylabel('Misses')
        plt.show()

    #
    # NN logic
    #

    def create_new_neural_network(self):
        file = shelve.open('data.txt')
        nn = neuralnetwork.NeuralNetwork(INPUT_NODES, HIDDEN_NODES, OUTPUT_NODES, LEARNING_RATE)
        file['nn'] = nn
        file['solved'] = 0
        file['results'] = []
        self.neural_network = nn
        self.boards_solved = 0
        self.neural_network_results = CompressedList()
        self.solved_label['text'] = 'Boards solved: 0'
        file.close()

    def train_neural_network(self):
        global TRAINING
        TRAINING = True
        while TRAINING:
            self.solve_with_neural_network()
            self.battlefield.refresh()
            self.root.update()

        with shelve.open('data.txt') as file:
            file['nn'] = self.neural_network
            file['solved'] = self.boards_solved
            file['results'] = self.neural_network_results

    def show_confidence(self):
        global SHOW_CONFIDENCE
        if SHOW_CONFIDENCE:
            SHOW_CONFIDENCE = False
            self.root_geometry(WIDTH, HEIGHT)
            self.place_buttons(X_INDENT, Y_INDENT)
            self.battlefield.frame.place(relx=NORMAL_FRAME_X_INDENT, rely=NORMAL_FRAME_Y_INDENT, anchor='center')
            self.battlefield.resize_cells(CELL_WIDTH, CELL_HEIGHT)
        else:
            SHOW_CONFIDENCE = True
            self.root_geometry(STRETCHED_WIDTH, STRETCHED_HEIGHT)
            self.place_buttons(STRETCHED_X_INDENT, STRETCHED_Y_INDENT)
            self.battlefield.frame.place(relx=STRETCHED_FRAME_X_INDENT, rely=STRETCHED_FRAME_Y_INDENT, anchor='center')
            self.battlefield.resize_cells(STRETCHED_CELL_WIDTH, STRETCHED_CELL_HEIGHT)
        self.root.update()

    def solve_with_neural_network(self):
        # Get NN from file
        """
        What I show to NN:
        Revealed damaged ships around a cell
        Heuristic
        NN processes each cell separately
        """
        while self.battlefield.player.parts_alive > 0:
            nn_input = None
            nn_answer = (None, None)
            maximum_confidence = 0.0
            for i in range(X_TILES):
                for j in range(Y_TILES):
                    if self.battlefield.cells[i][j]['bg'] == 'Grey':
                        # Seek for damaged ships
                        ships = []
                        for i_shift, j_shift in SHIFTS:
                            shifted_i = i + i_shift
                            shifted_j = j + j_shift
                            if not tile_exists(shifted_i, shifted_j):
                                ships.append(0.01)
                            else:
                                if self.battlefield.cells[shifted_i][shifted_j]['bg'] == HIT_COLOUR:
                                    ships.append(0.99)
                                else:
                                    ships.append(0.01)

                        nn_input = ships + [HEURISTIC_CENTER[i][j], HEURISTIC_CHESS[i][j]]
                        confidence = float(self.neural_network.query(nn_input))
                        if confidence > maximum_confidence:
                            nn_answer = (i, j)
                            maximum_confidence = confidence
                        self.battlefield.cells[i][j]['bg'] = 'Grey'
                        if SHOW_CONFIDENCE:
                            self.battlefield.cells[i][j]['text'] = '{:.2f}%'.format(maximum_confidence * 100)
                        if ENTERTAIN:
                            self.root.update()
            if SHOW_CONFIDENCE:
                self.root.update()
                sleep(CONFIDENCE_DELAY)
            self.battlefield.click_logic(nn_answer[0], nn_answer[1])
            correct_answer = [1] if self.battlefield.cells[nn_answer[0]][nn_answer[1]]['bg'] == HIT_COLOUR else [0]
            self.neural_network.train(nn_input, correct_answer)
            sleep(ENTERTAIN_DELAY)

        result = sum([sum([1 if cell['bg'] == MISS_COLOUR else 0
                      for cell in cell_row])
                      for cell_row in self.battlefield.cells])
        self.neural_network_results.add(result)
        self.boards_solved += 1
        self.solved_label['text'] = 'Boards solved: {}'.format(self.boards_solved)


def stop_training():
    global TRAINING
    TRAINING = False


def show_solution():
    global ENTERTAIN
    ENTERTAIN = False if ENTERTAIN else True


gui = MyGUI()

tk.mainloop()
