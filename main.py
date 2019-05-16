import tkinter as tk
from random import randint

X_TILES = 10
Y_TILES = 10
WIDTH = 35 * X_TILES
HEIGHT = 45 * Y_TILES
FRAME_WIDTH = 300
FRAME_HEIGHT = 300
BUTTON_WIDTH = FRAME_WIDTH // X_TILES // 100
BUTTON_HEIGHT = FRAME_HEIGHT // Y_TILES // 100
SHIP_TYPES = 4 + 1
HORIZONTAL = 'horizontal'
VERTICAL = 'vertical'

SHIFTS = ((-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1))

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
        for number in range(1, SHIP_TYPES):
            self.place_ship(SHIP_TYPES - number, colour, number)

    def place_ship(self, size, colour, to_place):

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
                    replace = self.grid.check_tiles_around(x_pos, y)
                    if replace:
                        break
                if not replace:
                    # print('Ship of size {} at:'.format(size))
                    for y in range(y_pos, y_pos + size):
                        # print(x_pos, y)
                        self.grid.cells[x_pos][y]['bg'] = colour
                        self.grid.taken[x_pos][y] = True

            elif rotation is VERTICAL:
                x_pos = randint(0, X_TILES - size)
                y_pos = randint(0, Y_TILES - 1)

                # Проверка
                for x in range(x_pos, x_pos + size):
                    replace = self.grid.check_tiles_around(x, y_pos)
                    if replace:
                        break
                if not replace:
                    # print('Ship of size {} at:'.format(size))
                    for x in range(x_pos, x_pos + size):
                        self.grid.cells[x][y_pos]['bg'] = colour
                        self.grid.taken[x][y_pos] = True

            if not replace:
                self.ships.append(Ship(x_pos, y_pos, size, rotation))
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
    def __init__(self):
        self.cells = [[tk.Button(master=frame, bg='Grey', bd=1, width=BUTTON_WIDTH, height=BUTTON_HEIGHT)
                       for _ in range(Y_TILES)] for _ in range(X_TILES)]

        self.taken = [[False for _ in range(Y_TILES)] for _ in range(X_TILES)]

        for x in range(X_TILES):
            for y in range(Y_TILES):
                self.cells[x][y].config(command=lambda i=x, j=y: self.click_logic(i, j))
                self.cells[x][y].grid(row=x, column=y)
        self.players = []

    def check_tiles_around(self, x, y):
        for x_shift, y_shift in SHIFTS:
            shifted_x = x + x_shift
            shifted_y = y + y_shift
            if tile_exists(shifted_x, shifted_y):
                if self.taken[x + x_shift][y + y_shift]:
                    return True
        return False

    def click_logic(self, i, j):
        self.cells[i][j]['text'] = 'i:{} j:{}'.format(i, j)
        if self.taken[i][j]:
            self.cells[i][j]['bg'] = 'Red'
            single = not self.check_tiles_around(i, j)
            if single:
                for i_shift, j_shift in SHIFTS:
                    shifted_i = i + i_shift
                    shifted_j = j + j_shift
                    if tile_exists(shifted_i, shifted_j):
                        self.cells[shifted_i][shifted_j].config(bg='Cyan', state='disabled')
        else:
            self.cells[i][j]['bg'] = 'Cyan'
        self.cells[i][j]['state'] = 'disabled'

    def add_player(self, colour):
        self.players.append(Fleet(self, colour))

    def refresh(self):
        players_buff = self.players
        self.__init__()
        # После повторной инициализации лист игроков очищается
        for player in players_buff:
            self.add_player(player.colour)
        # Нужно говорить программе какого именно игрока прятать и показывать
        # Без этих двух строчек снизу кнопка refresh работает как кнопка hide
        hide_button['command'] = self.players[0].hide
        reveal_button['command'] = self.players[0].reveal


root = tk.Tk()
root.geometry('{}x{}'.format(HEIGHT, WIDTH))

frame = tk.Frame(root, width=FRAME_WIDTH, height=FRAME_HEIGHT)
frame.place(relx=0.6, rely=0.5, anchor='center')

battlefield = Grid()

battlefield.add_player('yellow')

hide_button = tk.Button(master=root, bg='Grey', width=6, height=3, bd=1,
                        command=battlefield.players[0].hide, text='Hide')
hide_button.place(relx=0.05, rely=0.1)

reveal_button = tk.Button(master=root, bg='Grey', width=6, height=3, bd=1,
                          command=battlefield.players[0].reveal, text='Reveal')
reveal_button.place(relx=0.05, rely=0.3)

refresh_button = tk.Button(master=root, bg='Grey', width=6, height=3, bd=1,
                           command=battlefield.refresh, text='Refresh')
refresh_button.place(relx=0.05, rely=0.5)

tk.mainloop()
