# TODO:
#  1) Neural network does not learn shit.
#  2) I definitely should implement genetic selection algorithm
#  because there is nothing that punishes neural network for
#  solving the grid in maximum possible amount of turns.

import neuralnetwork
import tkinter as tk
import shelve
from complist import CompressedList
from constants import *
from grid import Grid, tile_exists
from matplotlib import pyplot as plt
from time import sleep


def stop_training():
    global TRAINING
    TRAINING = False


def show_solution():
    global ENTERTAIN
    ENTERTAIN = False if ENTERTAIN else True


class MyGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root_geometry(WIDTH, HEIGHT)

        self.frame = tk.Frame(master=self.root, width=FRAME_WIDTH, height=FRAME_HEIGHT)
        self.battlefield = Grid(self.frame)

        self.frame.place(relx=NORMAL_FRAME_X_INDENT, rely=NORMAL_FRAME_Y_INDENT, anchor='center')

        with shelve.open('data.txt') as file:
            self.neural_network = file['nn']
            self.boards_solved = file['solved']
            # Number of misses in games
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
        games_played = [int(n * self.neural_network_results.power) for n in range(1, len(results) + 1)]
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
            self.battlefield.stretched = False
            self.root_geometry(WIDTH, HEIGHT)
            self.place_buttons(X_INDENT, Y_INDENT)
            self.battlefield.frame.place(relx=NORMAL_FRAME_X_INDENT, rely=NORMAL_FRAME_Y_INDENT, anchor='center')
            self.battlefield.resize_cells(CELL_WIDTH, CELL_HEIGHT)
        else:
            SHOW_CONFIDENCE = True
            self.battlefield.stretched = True
            self.root_geometry(STRETCHED_WIDTH, STRETCHED_HEIGHT)
            self.place_buttons(STRETCHED_X_INDENT, STRETCHED_Y_INDENT)
            self.battlefield.frame.place(relx=STRETCHED_FRAME_X_INDENT, rely=STRETCHED_FRAME_Y_INDENT, anchor='center')
            self.battlefield.resize_cells(STRETCHED_CELL_WIDTH, STRETCHED_CELL_HEIGHT)

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


gui = MyGUI()

tk.mainloop()
