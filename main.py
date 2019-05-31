import tkinter as tk
import shelve
from complist import CompressedList
from copy import deepcopy
from constants import *
from grid import Grid, tile_exists
from matplotlib import pyplot as plt
from time import sleep


def stop_solving():
    global SOLVING
    SOLVING = False


def show_solution():
    global SOLUTION
    SOLUTION = False if SOLUTION else True


class Statistics:
    def __init__(self):
        self.results = CompressedList()
        self.best = X_TILES * Y_TILES
        self.worst = 0
        self.boards_solved = 0


class MyGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root_geometry(WIDTH, HEIGHT)
        self.root.title('Battleship game')

        self.grid_frame = tk.Frame(master=self.root, width=GRID_WIDTH, height=GRID_HEIGHT)
        self.battlefield = Grid(self.grid_frame)

        self.grid_frame.place(relx=NORMAL_FRAME_X_INDENT, rely=NORMAL_FRAME_Y_INDENT, anchor='center')

        self.buttons_frame = tk.Frame(master=self.root, width=BUTTON_FRAME_WIDTH, height=BUTTON_FRAME_HEIGHT)

        with shelve.open(FILE_NAME) as file:
            if 'stats' in file:
                self.stats = file['stats']
            else:
                self.stats = Statistics()
                file['stats'] = self.stats

        self.UI_buttons = {'dummy': tk.Button(text='Dummy'),
                           'refresh': tk.Button(text='Refresh\nboard', command=self.battlefield.refresh),
                           'hide': tk.Button(text='Show/hide\nfleet', command=self.battlefield.show_player),
                           'solution': tk.Button(text='Show\nsolution', command=show_solution),
                           'recreate': tk.Button(text='Dummy'),
                           'stop': tk.Button(text='Stop\nsolving', command=stop_solving),
                           'solve': tk.Button(text='Solve', command=self.solve),
                           'results': tk.Button(text='Refresh\nresults', command=self.refresh_results),
                           'plot': tk.Button(text='Results\nplot', command=self.show_results),
                           'exit': tk.Button(text='Exit', command=self.finish)}

        self.buttons_matrix = [list(self.UI_buttons.values())[i:i + BUTTONS_PER_COLUMN]
                               for i in range(0, len(self.UI_buttons), BUTTONS_PER_COLUMN)]

        self.config_buttons(BUTTON_WIDTH, BUTTON_HEIGHT, BUTTON_BORDER, BUTTON_COLOUR)

        self.place_buttons()

        self.solved_label = tk.Label(text='Solved: {}'.format(self.stats.boards_solved))
        self.solved_label.place(relx=0.71, rely=0.9)

        self.best_label = tk.Label(text='Best: {}'.format(self.stats.best))
        self.best_label.place(relx=0.41, rely=0.9)

        self.worst_label = tk.Label(text='Worst: {}'.format(self.stats.worst))
        self.worst_label.place(relx=0.56, rely=0.9)

    def save_results(self):
        with shelve.open(FILE_NAME) as file:
            file['stats'] = self.stats

    def refresh_results(self):
        self.solved_label['text'] = 'Solved: 0'
        self.best_label['text'] = 'Best: 100'
        self.worst_label['text'] = 'Worst: 0'
        self.stats = Statistics()
        self.save_results()

    def finish(self):
        self.save_results()
        for button in self.UI_buttons.values():
            button.destroy()
        for cell_row in self.battlefield.cells:
            for cell in cell_row:
                cell.destroy()
        self.grid_frame.destroy()
        self.buttons_frame.destroy()
        self.root.destroy()

    def root_geometry(self, width, height):
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = int((screen_width / 2) - (width / 2))
        y = int((screen_height / 2) - (height / 2))
        self.root.geometry('{:d}x{:d}+{:d}+{:d}'.format(width, height, x, y))

    def place_buttons(self):
        for x, button_row in enumerate(self.buttons_matrix):
            for y, button in enumerate(button_row):
                button.grid(row=y, column=x)

    def config_buttons(self, width, height, border, colour):
        for UI_button in self.UI_buttons.values():
            UI_button.config(width=width, height=height, bd=border, bg=colour)

    def draw_plot(self):
        games_played = [int(n * self.stats.results.power) for n in range(1, len(self.stats.results) + 1)]
        plt.plot(games_played, self.stats.results)
        plt.title('Game history')
        plt.xlabel('Games played')
        plt.ylabel('Misses')

    def show_results(self):
        self.draw_plot()
        plt.show()

    #
    # Solution logic
    #

    def solve(self):
        global SOLVING
        SOLVING = True
        solved_after_autosave = 0
        while SOLVING:
            self.solve_one()
            self.battlefield.refresh()
            self.root.update()
            solved_after_autosave += 1
            if solved_after_autosave >= GAMES_TO_AUTOSAVE:
                self.save_results()

    def get_biggest_ship_size(self):
        for size, type_destroyed in zip(range(len(self.battlefield.player.destroyed), 0, -1),
                                        self.battlefield.player.destroyed[::-1]):
            if type_destroyed < 1:  # 'type_destroyed' is a float
                return size

    def solve_one(self):
        confidence_grid = deepcopy(HEURISTIC_SUMMARY)
        current_order = 1

        only_one_sized_ships_left = False
        while self.battlefield.player.parts_alive > 0:
            switch_to_chess_order1 = 0
            switch_to_chess_order2 = 0

            # Detecting the biggest ship
            biggest_ship_size = self.get_biggest_ship_size()

            if biggest_ship_size == 1 and not only_one_sized_ships_left:
                for i in range(X_TILES):
                    for j in range(Y_TILES):
                        if (confidence_grid[i][j] > 0 and
                           self.battlefield.cells[i][j]['bg'] == DEFAULT_COLOUR):
                            new_confidence = 1

                            for i_shift, j_shift in SHIFTS_AROUND:
                                i_shifted = i + i_shift
                                j_shifted = j + j_shift
                                if (tile_exists(i_shifted, j_shifted) and
                                   self.battlefield.cells[i_shifted][j_shifted]['bg'] == DEFAULT_COLOUR):
                                    new_confidence += 1

                            confidence_grid[i][j] = new_confidence
            else:
                for i in range(X_TILES):
                    for j in range(Y_TILES):
                        if self.battlefield.cells[i][j]['bg'] != DEFAULT_COLOUR:
                            if (i + j + 1) % 2 == 0:
                                switch_to_chess_order1 += 1
                            else:
                                switch_to_chess_order2 += 1

                if current_order == 2 and switch_to_chess_order1 > switch_to_chess_order2:
                    confidence_grid += HEURISTIC_CHESS1 - HEURISTIC_CHESS2
                    current_order = 1

                elif current_order == 1 and switch_to_chess_order2 > switch_to_chess_order1:
                    confidence_grid += HEURISTIC_CHESS2 - HEURISTIC_CHESS1
                    current_order = 2

            maximum_confidence = 0
            answer = (None, None)
            for i in range(X_TILES):
                for j in range(Y_TILES):
                    if self.battlefield.cells[i][j]['bg'] == DEFAULT_COLOUR:
                        if confidence_grid[i][j] > maximum_confidence:
                            answer = (i, j)
                            maximum_confidence = confidence_grid[i][j]
            x, y = answer

            # Computing if it should continue shooting in that direction
            # e.g. you should not continue shooting 4 or more tiles in a row
            # if you have already sank a 4-sized ship
            for x_shift, y_shift in SHIFTS_HORIZONTAL_VERTICAL:
                x_shifted = x + x_shift
                y_shifted = y + y_shift

                if (tile_exists(x_shifted, y_shifted) and
                        self.battlefield.cells[x_shifted][y_shifted]['bg'] == HIT_COLOUR):
                    parts_hit = 0

                    # Counting parts hit leading to this cell
                    for times in range(1, 5):
                        x_shifted = x + x_shift * times
                        y_shifted = y + y_shift * times
                        if tile_exists(x_shifted, y_shifted):
                            if self.battlefield.cells[x_shifted][y_shifted]['bg'] != HIT_COLOUR:
                                break
                            else:
                                parts_hit += 1

                    # Detecting the biggest ship
                    biggest_ship_size = self.get_biggest_ship_size()

                    if parts_hit == SHIP_TYPES or parts_hit >= biggest_ship_size:
                        confidence_grid[x][y] -= X_TILES * Y_TILES * 100

            if confidence_grid[x][y] > 0:
                self.battlefield.click_logic(x, y)

            if self.battlefield.cells[x][y]['bg'] == HIT_COLOUR:
                # Ship can't be placed diagonally
                for x_shift, y_shift in SHIFTS_DIAGONAL:
                    x_shifted = x + x_shift
                    y_shifted = y + y_shift

                    if tile_exists(x_shifted, y_shifted):
                        confidence_grid[x_shifted][y_shifted] -= X_TILES * Y_TILES * 100

                # Ship can be placed horizontally or vertically
                for x_shift, y_shift in SHIFTS_HORIZONTAL_VERTICAL:
                    x_shifted = x + x_shift
                    y_shifted = y + y_shift

                    if tile_exists(x_shifted, y_shifted):
                        confidence_grid[x_shifted][y_shifted] += SHIP_TYPES * 4

            if SOLUTION:
                self.root.update()
                sleep(SOLUTION_DELAY)

        # Calculating amount of misses
        result = sum([sum([1 if cell['bg'] == MISS_COLOUR else 0
                      for cell in cell_row])
                      for cell_row in self.battlefield.cells])

        self.stats.results.append(result)
        self.stats.boards_solved += 1

        if result < self.stats.best:
            self.stats.best = result
            self.best_label['text'] = 'Best: {}'.format(result)
        if result > self.stats.worst:
            self.stats.worst = result
            self.worst_label['text'] = 'Worst: {}'.format(result)

        self.solved_label['text'] = 'Solved: {}'.format(self.stats.boards_solved)


gui = MyGUI()

tk.mainloop()
