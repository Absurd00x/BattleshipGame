import tkinter as tk
from constants import *
from grid import Grid, tile_exists
from random import randint
from tkinter import messagebox


class Statistics:
    def __init__(self):
        self.player_score = 0
        self.bot_score = 0


class MyGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root_geometry(WIDTH, HEIGHT)
        self.root.title('Battleship game')
        self.root.resizable(width=False, height=False)

        self.player_frame = tk.Frame(master=self.root)
        self.player_field = Grid(self.player_frame)
        self.player_field.show_player()
        self.player_field.flip_click_logic()

        self.player_frame.place(relx=PLAYER_GRID_X, rely=GRID_Y, anchor='center')

        self.bot_frame = tk.Frame(master=self.root)
        self.bot_field = Grid(self.bot_frame)
        self.bot_frame.place(relx=BOT_GRID_X, rely=GRID_Y, anchor='center')
        self.bot_field.lock()

        self.button_frame = tk.Frame(master=self.root)

        self.UI_buttons = {'new game': tk.Button(self.button_frame, text='New\ngame', command=self.new_game),
                           'place': tk.Button(self.button_frame, text='Place\nrandomly',
                                              command=self.place_ships),
                           'play': tk.Button(self.button_frame, text='Play!', command=self.play),
                           'exit': tk.Button(self.button_frame, text='Exit', command=self.finish)}

        self.buttons_matrix = [list(self.UI_buttons.values())[i:i + BUTTONS_PER_COLUMN]
                               for i in range(0, len(self.UI_buttons), BUTTONS_PER_COLUMN)]

        self.config_buttons(BUTTON_WIDTH, BUTTON_HEIGHT, BUTTON_BORDER, BUTTON_COLOUR)

        self.place_buttons()
        self.button_frame.place(relx=BUTTON_FRAME_X, rely=BUTTON_FRAME_Y)

        self.player_label = tk.Label(self.root, text='Your field')
        self.player_label.place(relx=PLAYER_LABEL_X, rely=BELONG_LABEL_Y)

        self.bot_label = tk.Label(self.root, text='Computers field')
        self.bot_label.place(relx=BOT_LABEL_X, rely=BELONG_LABEL_Y)
        self.bot_turn = self.bot_init()

        self.statistics_label = tk.Label(self.root, text='Statistics')
        self.statistics_label.place(relx=STATISTICS_LABEL_X, rely=STATISTICS_LABEL_Y)

        self.stats = Statistics()

        try:
            with open(FILE_NAME, 'r') as file:
                self.stats.player_score = int(file.readline())
                self.stats.bot_score = int(file.readline())
        except:
            with open(FILE_NAME, 'w') as file:
                file.write('0\n0')
            self.stats.player_score = 0
            self.stats.bot_score = 0

        self.player_score_label = tk.Label(self.root, text='Player score: {}'.format(self.stats.player_score))
        self.player_score_label.place(relx=SCORE_LABEL_X, rely=PLAYER_SCORE_LABEL_Y)

        self.bot_score_label = tk.Label(self.root, text='Bot score: {}'.format(self.stats.bot_score))
        self.bot_score_label.place(relx=SCORE_LABEL_X, rely=BOT_SCORE_LABEL_Y)

        self.winrate_label = tk.Label(self.root, text='Winrate: {}%'.format(
            int((self.stats.player_score / max(1, (self.stats.player_score + self.stats.bot_score))) * 100)))
        self.winrate_label.place(relx=SCORE_LABEL_X, rely=WINRATE_LABEL_Y)

        self.info_label = tk.Label(self.root,
                                   text='Bot was solving randomly\ngenerated boards\nmissing 43 times on average')
        self.info_label.place(relx=SCORE_LABEL_X, rely=INFO_LABEL_Y)

        self.over = False

    def play(self):
        if not self.over:
            if not self.player_field.check_ships():
                messagebox.showerror("Error", "Ships placed inappropriately")
            else:
                self.player_field.flip_click_logic()
                self.bot_field.unlock()
                self.player_field.lock()
                for x in range(X_TILES):
                    for y in range(Y_TILES):
                        self.bot_field.cells[x][y]['command'] = lambda i=x, j=y: self.player_click_logic(i, j)
                turn = 'player' if randint(0, 1) else 'bot'
                if turn == 'player':
                    messagebox.showinfo("It's your turn", "You go first!")
                if turn == 'bot':
                    self.bot_turn()

    def new_game(self):
        if self.over:
            self.over = False

            self.bot_field.refresh()
            self.bot_field.lock()

            self.player_field.refresh()
            self.player_field.show_player()
            self.player_field.flip_click_logic()

            self.bot_turn = self.bot_init()

    def refresh_stats(self):
        self.player_score_label['text'] = 'Player score: {}'.format(self.stats.player_score)
        self.bot_score_label['text'] = 'Bot score: {}'.format(self.stats.bot_score)
        self.winrate_label['text'] = 'Winrate: {}%'.format(
            int((self.stats.player_score / max(1, (self.stats.player_score + self.stats.bot_score))) * 100))

    def game_over(self, winner):
        self.over = True
        self.bot_field.lock()

        if winner == 'player':
            self.stats.player_score += 1
            messagebox.showinfo("Congratulations!", "You have beaten the computer!")
        else:
            self.stats.bot_score += 1
            self.bot_field.show_player()
            answer = 'yes' if messagebox.askyesno("Defeat", "You have been defeated\nRematch?") else 'no'
            if answer == 'yes':
                self.new_game()
        self.refresh_stats()

    def player_click_logic(self, i, j):
        self.bot_field.click_logic(i, j)

        if self.bot_field.player.parts_alive == 0:
            self.game_over('player')
        else:
            self.bot_turn()
            if self.player_field.player.parts_alive == 0:
                self.game_over('computer')

    def place_ships(self):
        self.player_field.refresh()
        self.player_field.show_player()
        self.player_field.flip_click_logic()

    def root_geometry(self, width, height):
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = int((screen_width / 2) - (width / 2))
        y = int((screen_height / 2) - (height / 2))
        self.root.geometry('{:d}x{:d}+{:d}+{:d}'.format(width, height, x, y))

    def place_buttons(self):
        for x, button_row in enumerate(self.buttons_matrix):
            for y, button in enumerate(button_row):
                button.grid(padx=0, pady=0, ipadx=0, ipady=0, row=y, column=x)

    def config_buttons(self, width, height, border, colour):
        for UI_button in self.UI_buttons.values():
            UI_button.config(width=width, height=height, bd=border, bg=colour)

    def finish(self):
        with open(FILE_NAME, 'w') as file:
            file.write('{}\n{}'.format(self.stats.player_score, self.stats.bot_score))

        self.root.destroy()

    #
    # Solution logic
    #

    def get_biggest_ship_size(self):
        for size, type_destroyed in zip(range(len(self.player_field.player.destroyed), 0, -1),
                                        self.player_field.player.destroyed[::-1]):
            if type_destroyed < 1:  # 'type_destroyed' is a float
                return size

    def bot_init(self):
        current_order = randint(1, 2)
        if current_order == 1:
            confidence_grid = [[HEURISTIC_CENTER[i][j] + HEURISTIC_CHESS1[i][j]
                               for j in range(Y_TILES)]
                               for i in range(X_TILES)]
        elif current_order == 2:
            confidence_grid = [[HEURISTIC_CENTER[i][j] + HEURISTIC_CHESS2[i][j]
                                for j in range(Y_TILES)]
                               for i in range(X_TILES)]

        only_one_sized_ships_left = False

        shot = [[False for _ in range(Y_TILES)] for _ in range(X_TILES)]

        def make_turn():
            nonlocal confidence_grid, current_order, only_one_sized_ships_left, shot
            if self.player_field.player.parts_alive > 0:
                switch_to_chess_order1 = 0
                switch_to_chess_order2 = 0

                # Detecting the biggest ship
                biggest_ship_size = self.get_biggest_ship_size()

                if biggest_ship_size == 1 and not only_one_sized_ships_left:
                    for i in range(X_TILES):
                        for j in range(Y_TILES):
                            if confidence_grid[i][j] > 0 and not shot[i][j]:
                                new_confidence = 1

                                for i_shifted, j_shifted in apply_shift(i, j, SHIFTS_AROUND):
                                    if not self.player_field.player.taken[i_shifted][j_shifted]:
                                        new_confidence += 1

                                confidence_grid[i][j] = new_confidence
                else:
                    for i in range(X_TILES):
                        for j in range(Y_TILES):
                            if shot[i][j]:
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
                        if not shot[i][j]:
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
                            self.player_field.cells[x_shifted][y_shifted]['bg'] == HIT_COLOUR):
                        parts_hit = 0

                        # Counting parts hit leading to this cell
                        for times in range(1, 5):
                            x_shifted = x + x_shift * times
                            y_shifted = y + y_shift * times
                            if tile_exists(x_shifted, y_shifted):
                                if self.player_field.cells[x_shifted][y_shifted]['bg'] != HIT_COLOUR:
                                    break
                                else:
                                    parts_hit += 1

                        # Detecting the biggest ship
                        biggest_ship_size = self.get_biggest_ship_size()

                        if parts_hit == SHIP_TYPES or parts_hit >= biggest_ship_size:
                            confidence_grid[x][y] -= X_TILES * Y_TILES * 100

                if confidence_grid[x][y] > 0:
                    self.player_field.click_logic(x, y)
                    shot[x][y] = True

                    if self.player_field.cells[x][y]['bg'] == HIT_COLOUR:
                        # Ship can't be placed diagonally
                        for x_shifted, y_shifted in apply_shift(x, y, SHIFTS_DIAGONAL):
                            confidence_grid[x_shifted][y_shifted] -= X_TILES * Y_TILES * 100

                        # Ship can be placed horizontally or vertically
                        for x_shifted, y_shifted in apply_shift(x, y, SHIFTS_HORIZONTAL_VERTICAL):
                            confidence_grid[x_shifted][y_shifted] += SHIP_TYPES * 4
                else:
                    make_turn()

        return make_turn


gui = MyGUI()

tk.mainloop()
