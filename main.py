import tkinter as tk
from random import randint

X_TILES = 10
Y_TILES = 10
WIDTH = 35 * X_TILES
HEIGHT = 45 * Y_TILES
FRAME_WIDTH = 300
FRAME_HEIGHT = 300
BUTTON_WIDTH = FRAME_WIDTH // X_TILES // 100
BUTTON_HEIGTH = FRAME_HEIGHT // Y_TILES // 100

SHIFTS = ((-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1))


def tile_exists(x, y):
    return -1 < x < X_TILES and -1 < y < Y_TILES


def check_tiles_around(x, y):
    for x_shift, y_shift in SHIFTS:
        shifted_x = x + x_shift
        shifted_y = y + y_shift
        if tile_exists(shifted_x, shifted_y):
            if taken[x + x_shift][y + y_shift]:
                return True
    return False


def place_ship(size, colour, to_place):

    placed = 0
    parameters = (size, [])

    while placed < to_place:
        replace = False
        x_pos, y_pos = None, None
        rotation = 'horizontal' if randint(0, 1) else 'vertical'
        if rotation is 'horizontal':
            x_pos = randint(0, X_TILES - 1)
            y_pos = randint(0, Y_TILES - size)

            # Сначала проверяем - не задеваем ли мы другой корабль такой постановкой
            for y in range(y_pos, y_pos + size):
                replace = check_tiles_around(x_pos, y)
                if replace:
                    break
            if not replace:
                for y in range(y_pos, y_pos + size):
                    button_set[x_pos][y]['bg'] = colour
                    taken[x_pos][y] = True

        elif rotation is 'vertical':
            x_pos = randint(0, X_TILES - size)
            y_pos = randint(0, Y_TILES - 1)

            # Проверка
            for x in range(x_pos, x_pos + size):
                replace = check_tiles_around(x, y_pos)
                if replace:
                    break
            if not replace:
                for x in range(x_pos, x_pos + size):
                    button_set[x][y_pos]['bg'] = colour
                    taken[x][y_pos] = True

        if not replace:
            placed += 1
            parameters[1].append((x_pos, y_pos, rotation))
    return parameters


class Ship:
    def __init__(self, x, y, size, rotation):
        self.x = x
        self.y = y
        self.size = size
        self.rotation = rotation


class Fleet:
    def __init__(self, colour):
        self.ships = []
        self.colour = colour
        for number in range(1, 5):
            size, coordinates = place_ship(5 - number, colour, number)
            for x, y, rotation in coordinates:
                self.ships.append(Ship(x, y, size, rotation))

    def hide(self):
        for ship in self.ships:
            if ship.rotation is 'horizontal':
                for y_pos in range(ship.y, ship.y + ship.size):
                    if button_set[ship.x][y_pos]['bg'] != 'Red':
                        button_set[ship.x][y_pos]['bg'] = 'Grey'
            elif ship.rotation is 'vertical':
                for x_pos in range(ship.x, ship.x + ship.size):
                    if button_set[x_pos][ship.y]['bg'] != 'Red':
                        button_set[x_pos][ship.y]['bg'] = 'Grey'

    def reveal(self):
        for ship in self.ships:
            if ship.rotation is 'horizontal':
                for y_pos in range(ship.y, ship.y + ship.size):
                    if button_set[ship.x][y_pos]['bg'] == 'Grey':
                        button_set[ship.x][y_pos]['bg'] = self.colour
            elif ship.rotation is 'vertical':
                for x_pos in range(ship.x, ship.x + ship.size):
                    if button_set[x_pos][ship.y]['bg'] == 'Grey':
                        button_set[x_pos][ship.y]['bg'] = self.colour


def click_logic(button, x, y):
    if taken[x][y]:
        button['bg'] = 'Red'
    else:
        button['bg'] = 'Cyan'
    button['state'] = 'disabled'


root = tk.Tk()
root.geometry('{}x{}'.format(HEIGHT, WIDTH))

frame = tk.Frame(root, width=FRAME_WIDTH, height=FRAME_HEIGHT)
frame.place(relx=0.6, rely=0.5, anchor='center')

button_set = [[tk.Button(master=frame, bg='Grey', bd=1, width=BUTTON_WIDTH, height=BUTTON_HEIGTH)
               for _ in range(Y_TILES)] for _ in range(X_TILES)]

for x in range(X_TILES):
    for y in range(Y_TILES):
        button_set[x][y].config(command=lambda i=x, j=y: click_logic(button_set[i][j], i, j))
        button_set[x][y].grid(row=x, column=y)

# Логика

taken = [[False for _ in range(Y_TILES)] for _ in range(X_TILES)]

player1 = Fleet('yellow')

hide_button = tk.Button(master=root, bg='Grey', width=6, height=3, bd=1, command=player1.hide, text='Hide')
hide_button.place(relx=0.05, rely=0.1)

reveal_button = tk.Button(master=root, bg='Grey', width=6, height=3, bd=1, command=player1.reveal, text='Reveal')
reveal_button.place(relx=0.05, rely=0.3)

tk.mainloop()
