import curses
import os
import random


def set_shorter_esc_delay_in_os():
    os.environ.setdefault('ESCDELAY', '0')


tree = {
    "char": "T",
    "passable": False,
    "has_encounters": False
}

grass = {
    "char": '"',
    "passable": True,
    "has_encounters": True
}

mountain = {
    "char": "^",
    "passable": False,
    "has_encounters": False
}

water = {
    "char": "W",
    "passable": False,
    "has_encounters": True
}

empty = {
    "char": ".",
    "passable": True,
    "has_encounters": False
}

wall = {
    "char": "X",
    "passable": False,
    "has_encounters": False
}

gaussian_matrix = [(-3, 0.006), (-2, 0.061), (-1, 0.242), (0, 0.383), (1, 0.242), (2, 0.061), (3, 0.006)]


def create_heightmap(height, width):
    heightmap = [[0 for i in range(width)] for j in range(height)]

    for drop in range(200):
        center_y = random.randint(5, height-5)
        center_x = random.randint(5, width-5)
        for particle in range(random.randint(10, 25)):
            particle_y = random.randint(center_y - 2, center_y + 2)
            particle_x = random.randint(center_x - 2, center_x + 2)
            heightmap[particle_y][particle_x] += 1
            initial_height = heightmap[particle_y][particle_x]
            move_points = []
            for adjacent_x in [particle_x - 1, particle_x + 1]:
                for adjacent_y in [particle_y - 1, particle_y + 1]:
                    if heightmap[adjacent_y][adjacent_x] < initial_height - 1:
                        move_points.append((adjacent_y, adjacent_x))
            if len(move_points) > 0:
                heightmap[particle_y][particle_x] -= 1
                new_point = move_points[random.randint(0, len(move_points) - 1)]
                heightmap[new_point[0]][new_point[1]] += 1

    blurred_heightmap = [[0 for i in range(width)] for j in range(height)]
    for y, row in enumerate(heightmap):
        for x, cell in enumerate(row):
            for offset, multiplier in gaussian_matrix:
                if x + offset > 0 and x + offset < (width - 2):
                    blurred_heightmap[y][x] += heightmap[y][x + offset] * multiplier
                if y + offset > 0 and y + offset < (height - 2):
                    blurred_heightmap[y][x] += heightmap[y + offset][x] * multiplier
    return blurred_heightmap


def map_demo(screen):
    curses.curs_set(0)
    map_model = [[empty.copy() for x in range(140)] for y in range(119)]
    for y, row in enumerate(map_model):
        for x, tile in enumerate(row):
            if x <= 19 or y <= 9 or x >= 80 or y >= 90:
                map_model[y][x] = wall.copy()

    heightmap = create_heightmap(80, 60)
    for y, row in enumerate(heightmap):
        for x, height in enumerate(row):
            point_y = y + 10
            point_x = x + 20
            if height < 0.1:
                map_model[point_y][point_x] = water.copy()
            elif height >= 0.1 and height < 0.2:
                map_model[point_y][point_x] = grass.copy()
            elif height >= 0.2 and height < 1.95:
                map_model[point_y][point_x] = empty.copy()
            elif height >= 1.95 and height < 2.0:
                map_model[point_y][point_x] = grass.copy()
            elif height >= 2.0 and height < 2.3:
                map_model[point_y][point_x] = empty.copy()
            elif height >= 2.3 and height < 2.4:
                map_model[point_y][point_x] = grass.copy()
            elif height >= 2.4 and height < 3.1:
                map_model[point_y][point_x] = tree.copy()
            elif height >= 3.1:
                map_model[point_y][point_x] = mountain.copy()

    map = ''.join(str(tile["char"]) for rows in map_model for tile in rows)

    items = []

    topLeftY = 0
    topLeftX = 0

    mapHeight = 20
    mapWidth = 40

    map_pad = curses.newpad(120, 140)

    num_rows, num_cols = screen.getmaxyx()

    middle_row = int(num_rows / 2)
    half_width_of_map = int(mapWidth / 2)
    middle_column = int(num_cols / 2)
    x_position = middle_column - half_width_of_map
    half_height_of_map = int(mapHeight / 2)
    y_position = middle_row - half_height_of_map

    running = True
    while (running):
        map_pad.erase()
        map_pad.addstr(0, 0, map)
        curses.init_pair(1, curses.COLOR_RED, curses.COLOR_WHITE)
        player_x = topLeftX + half_width_of_map
        player_y = topLeftY + half_height_of_map
        for it in items:
            map_pad.addstr(it["y"], it["x"], it["char"])

        map_pad.addstr(player_y, player_x, '@', curses.color_pair(1))
        map_pad.refresh(topLeftY, topLeftX, y_position, x_position, y_position + mapHeight, x_position + mapWidth)

        try:
            c = screen.getkey()

            if (str(c) == '\x1b'):
                running = False
            if (str(c) == 'w'):
                topLeftY = max(0, topLeftY - 1)
            if (str(c) == 's'):
                topLeftY = min(79, topLeftY + 1)
            if (str(c) == 'a'):
                topLeftX = max(0, topLeftX - 1)
            if (str(c) == 'd'):
                topLeftX = min(59, topLeftX + 1)
        except:
            num_rows, num_cols = screen.getmaxyx()

            middle_row = int(num_rows / 2)
            half_width_of_map = int(mapWidth / 2)
            middle_column = int(num_cols / 2)
            x_position = middle_column - half_width_of_map
            half_height_of_map = int(mapHeight / 2)
            y_position = middle_row - half_height_of_map
            screen.erase()
            screen.refresh()


set_shorter_esc_delay_in_os()
curses.wrapper(map_demo)
