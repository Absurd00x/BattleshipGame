import tkinter as tk
from random import randint
from constants import *

#
# Ship
#


class Ship:
    def __init__(self, size):
        self.size = size
        self.health = size

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
        self.colour = SHIP_COLOUR
        # Displays ship size placed in a tile
        self.taken = [[0 for _ in range(Y_TILES)] for _ in range(X_TILES)]
        self.destroyed = [0 for _ in range(SHIP_TYPES)]
        self.ship_number = 1
        for number in range(1, SHIP_TYPES + 1):
            self.place_ship(SHIP_TYPES - number + 1, number)
        del self.ship_number
        self.parts_alive = TOTAL_PARTS
        self.shown = False

    def check_tiles_around(self, x, y):
        for x_shift, y_shift in SHIFTS_AROUND:
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
            rotation = HORIZONTAL if randint(0, 1) else VERTICAL
            if rotation is HORIZONTAL:
                x_pos = randint(0, X_TILES - 1)
                y_pos = randint(0, Y_TILES - size)

                # Checking if ships overlap
                for y in range(y_pos, y_pos + size):
                    replace = (self.check_tiles_around(x_pos, y)
                               or self.taken[x_pos][y])
                    if replace:
                        break
                if not replace:
                    for y in range(y_pos, y_pos + size):
                        self.taken[x_pos][y] = self.ship_number

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
                        self.taken[x][y_pos] = self.ship_number

            current_try += 1

            if not replace:
                self.ships.append(Ship(size))
                self.ship_number += 1
                placed += 1
                current_try = 0

#
# Grid
#


class Grid:
    def __init__(self, frame):
        self.frame = frame

        self.cells = [[tk.Button(master=self.frame, bg=DEFAULT_COLOUR, bd=1)
                       for _ in range(Y_TILES)] for _ in range(X_TILES)]

        self.player = Fleet()

        self.current_logic = 'preparation'
        self.flip_click_logic()
        self.place_cells()

    def bfs(self, i, j, visited):
        visited[i][j] = True
        queue = [(i, j)]
        cur_x, cur_y, size = None, None, 0
        while len(queue) > 0:
            size += 1
            cur_x, cur_y = queue.pop()
            for x_shifted, y_shifted in apply_shift(cur_x, cur_y, SHIFTS_HORIZONTAL_VERTICAL):
                if self.player.taken[x_shifted][y_shifted] and not visited[x_shifted][y_shifted]:
                    visited[x_shifted][y_shifted] = True
                    queue.append((x_shifted, y_shifted))

        return size

    def check_ships(self):
        for i in range(X_TILES):
            for j in range(Y_TILES):
                if self.player.taken[i][j]:
                    for i_shifted, j_shifted in apply_shift(i, j, SHIFTS_DIAGONAL):
                        if self.player.taken[i_shifted][j_shifted]:
                            return False

                    connection_count = 0

                    for i_shifted, j_shifted in apply_shift(i, j, SHIFTS_HORIZONTAL_VERTICAL):
                        if self.player.taken[i_shifted][j_shifted]:
                            connection_count += 1

                    if connection_count > 2:
                        return False
                    elif connection_count == 2:
                        # Checking if 2 "connected" tiles lie on a straight line
                        if not ((tile_exists(i + 1, j) and tile_exists(i - 1, j) and
                                self.player.taken[i + 1][j] and self.player.taken[i - 1][j]) or
                                (tile_exists(i, j + 1) and tile_exists(i, j - 1) and
                                self.player.taken[i][j + 1] and self.player.taken[i][j - 1])):
                            return False

        visited = [[False for _ in range(Y_TILES)] for _ in range(X_TILES)]
        sizes = {}
        for i in range(X_TILES):
            for j in range(Y_TILES):
                if self.player.taken[i][j] and not visited[i][j]:
                    size = self.bfs(i, j, visited)
                    if size in sizes:
                        sizes[size] += 1
                    else:
                        sizes[size] = 1

        correct_sizes = {1: False, 2: False, 3: False, 4: False}

        for size in sizes.keys():
            if size not in correct_sizes:
                return False
            else:
                correct_sizes[size] = True

        for present in correct_sizes.values():
            if not present:
                return False

        return sizes[4] == 1 and sizes[3] == 2 and sizes[2] == 3 and sizes[1] == 4

    def lock(self):
        for cell_row in self.cells:
            for cell in cell_row:
                cell['state'] = 'disabled'

    def unlock(self):
        for cell_row in self.cells:
            for cell in cell_row:
                if cell['bg'] == DEFAULT_COLOUR:
                    cell['state'] = 'normal'

    def show_player(self):
        if self.player.shown:
            self.hide()
            self.player.shown = False
        else:
            self.reveal()
            self.player.shown = True

    def hide(self):
        for i in range(X_TILES):
            for j in range(Y_TILES):
                if self.player.taken[i][j] and self.cells[i][j]['bg'] != HIT_COLOUR:
                    self.cells[i][j]['bg'] = DEFAULT_COLOUR

    def reveal(self):
        for i in range(X_TILES):
            for j in range(Y_TILES):
                if self.player.taken[i][j] and self.cells[i][j]['bg'] != HIT_COLOUR:
                    self.cells[i][j]['bg'] = SHIP_COLOUR

    def place_cells(self):
        for x in range(X_TILES):
            for y in range(Y_TILES):
                self.cells[x][y].grid(row=x, column=y)

    def flip_click_logic(self):
        if self.current_logic == 'default':
            self.current_logic = 'preparation'
            for x in range(X_TILES):
                for y in range(Y_TILES):
                    self.cells[x][y]['command'] = lambda i=x, j=y: self.prepare_click_logic(i, j)
        else:
            self.current_logic = 'default'
            for x in range(X_TILES):
                for y in range(Y_TILES):
                    self.cells[x][y]['command'] = lambda i=x, j=y: self.click_logic(i, j)

    def prepare_click_logic(self, i, j):
        if self.cells[i][j]['bg'] == SHIP_COLOUR:
            self.cells[i][j]['bg'] = DEFAULT_COLOUR
            self.player.taken[i][j] = 0
        else:
            self.cells[i][j]['bg'] = SHIP_COLOUR
            self.player.taken[i][j] = 1

    def click_logic(self, i, j):
        if self.player.taken[i][j]:
            ship_number = self.player.taken[i][j] - 1
            ship_size = self.player.ships[ship_number].size
            progress = {1: 0.25, 2: 0.34, 3: 0.5, 4: 1}
            self.cells[i][j]['bg'] = HIT_COLOUR
            self.player.parts_alive -= 1
            self.player.ships[ship_number].health -= 1
            if self.player.ships[ship_number].health == 0:
                self.player.destroyed[ship_size - 1] += progress[ship_size]
        else:
            self.cells[i][j]['bg'] = MISS_COLOUR
        self.cells[i][j]['state'] = 'disabled'
        self.cells[i][j].update()

    def refresh(self):
        # Stupid tkinter objects need to be destroyed manually
        for cell_row in self.cells:
            for cell in cell_row:
                cell.destroy()
        self.__init__(self.frame)
