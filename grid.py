import tkinter as tk
from random import randint
from constants import *

#
# Ship
#


class Ship:
    def __init__(self, x, y, size, rotation):
        self.x = x
        self.y = y
        self.size = size
        self.rotation = rotation
        self.health = size

#
# Fleet
#


def tile_exists(x, y):
    return -1 < x < X_TILES and -1 < y < Y_TILES


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
            x_pos, y_pos = None, None
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
                self.ships.append(Ship(x_pos, y_pos, size, rotation))
                self.ship_number += 1
                placed += 1
                current_try = 0

#
# Grid
#


class Grid:
    def __init__(self, frame, stretched=False):
        self.frame = frame
        self.stretched = stretched
        self.cells = None
        if stretched:
            self.fit_cells(STRETCHED_CELL_WIDTH, STRETCHED_CELL_HEIGHT)
        else:
            self.fit_cells(CELL_WIDTH, CELL_HEIGHT)

        self.player = Fleet()

    def fit_cells(self, width, height):
        self.cells = [[tk.Button(master=self.frame, bg=DEFAULT_COLOUR, bd=1, width=width, height=height)
                       for _ in range(Y_TILES)] for _ in range(X_TILES)]

        for x in range(X_TILES):
            for y in range(Y_TILES):
                self.cells[x][y].config(command=lambda i=x, j=y: self.click_logic(i, j))
                self.cells[x][y].grid(row=x, column=y)

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
                        self.cells[ship.x][y_pos]['bg'] = DEFAULT_COLOUR
            elif ship.rotation is VERTICAL:
                for x_pos in range(ship.x, ship.x + ship.size):
                    if self.cells[x_pos][ship.y]['bg'] != HIT_COLOUR:
                        self.cells[x_pos][ship.y]['bg'] = DEFAULT_COLOUR

    def reveal(self):
        for ship in self.player.ships:
            if ship.rotation is HORIZONTAL:
                for y_pos in range(ship.y, ship.y + ship.size):
                    if self.cells[ship.x][y_pos]['bg'] == DEFAULT_COLOUR:
                        self.cells[ship.x][y_pos]['bg'] = PLAYER_COLOUR
            elif ship.rotation is VERTICAL:
                for x_pos in range(ship.x, ship.x + ship.size):
                    if self.cells[x_pos][ship.y]['bg'] == DEFAULT_COLOUR:
                        self.cells[x_pos][ship.y]['bg'] = PLAYER_COLOUR

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

    def refresh(self):
        # Stupid tkinter objects need to be destroyed manually
        for cell_row in self.cells:
            for cell in cell_row:
                cell.destroy()
        self.__init__(self.frame, self.stretched)
