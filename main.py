import time
import math
import random
from typing import Self

import pygame as pg


class Game(object):

    _SCREEN_SIZE = (640, 480)
    _SCREEN_FLAGS = pg.RESIZABLE | pg.SCALED
    _GAME_SPEED = 60

    _BLACK = (0, 0, 0)
    _GREY = (128, 128, 128)
    _WHITE = (255, 255, 255)
    _RED = (255, 0, 0)
    _GREEN = (0, 255, 0)
    _BLUE = (0, 0, 255)
    _CYAN = (0, 255, 255)
    _MAGENTA = (255, 0, 255)
    _YELLOW = (255, 255, 0)

    _TILE_SIZE = 8
    _MAP_SIZE = (80, 60)
    _TILE_OFFSETS = (
        (0, -1),
        (-1, 0),
        (1, 0),
        (0, 1),
    )

    def __init__(self: Self) -> None:
        pg.init()

        self._settings = {
            'vsync': 1,
        }
        self._screen = pg.display.set_mode(
            self._SCREEN_SIZE,
            flags=self._SCREEN_FLAGS,
            vsync=self._settings['vsync']
        )
        pg.display.set_caption('Pathfinding')
        self._running = 0

        self._font = pg.font.SysFont('Arial', 20)
        
        self._map = []
        for y in range(self._MAP_SIZE[1]):
            self._map.append([0] * self._MAP_SIZE[0])
        # 0 = empty spac
        # 1 = obstacle
        self._start = (0, 0)
        self._end = (self._MAP_SIZE[0] - 1, self._MAP_SIZE[1] - 1)
        self._path = []
        self._algorithm = 'A*'

        self._solve_time = math.inf

    def _rect(self: Self, pos: list) -> pg.Rect:
        return pg.Rect(
            self._TILE_SIZE * pos[0], 
            self._TILE_SIZE * pos[1],
            self._TILE_SIZE,
            self._TILE_SIZE,
        )
    
    # Return manhattan distance
    def _manhattan(self: Self, pos1: list, pos2: list) -> int:
        return abs(pos2[0] - pos1[0]) + abs(pos2[1] - pos1[1])

    def _pathfind(self: Self) -> None:
        start = time.time()

        # Setup
        g = {}
        h = {}
        parent = {}
        visited = set()
        will = {self._start}
        for y in range(self._MAP_SIZE[1]):
            for x in range(self._MAP_SIZE[0]):
                node = (x, y)
                g[node] = math.inf
                h[node] = 0
                if self._algorithm == 'A*':
                    h[node] = self._manhattan(node, self._end)
                parent[node] = self._start
        g[self._start] = 0

        # Algorithm
        while will:
            # Find the node
            least = math.inf
            for tentative in will:
                f = g[tentative] + h[tentative]
                if f < least:
                    node = tentative
                    least = f
            will.remove(node)
            visited.add(node)

            if node == self._end:
                break
            
            # Check Neighbors
            for offset in self._TILE_OFFSETS:
                neighbor = (node[0] + offset[0], node[1] + offset[1])
                weight = 1
                tentative = g[node] + weight
                invalid = (
                    neighbor[0] < 0
                    or neighbor[1] < 0
                    or neighbor[0] >= self._MAP_SIZE[0]
                    or neighbor[1] >= self._MAP_SIZE[1]
                    or neighbor in visited
                    or self._map[neighbor[1]][neighbor[0]]
                    or tentative >= g[neighbor]
                )
                if invalid:
                    continue

                g[neighbor] = tentative
                parent[neighbor] = node
                will.add(neighbor)
        
        # Trace path back
        self._path = []
        node = self._end
        while parent[node] != self._start:
            node = parent[node]
            self._path.append(node)

        self._solve_time = time.time() - start
        
    # Prim's Algorithm Maze Generation
    def _generate(self: Self) -> None: 
        # Set all squares to white
        for y in range(self._MAP_SIZE[1]):
            for x in range(self._MAP_SIZE[0]):
                self._map[y][x] = 1
        # Generate Maze
        unvisited = set()
        for y in range(0, self._MAP_SIZE[1] - 1, 2):
            for x in range(0, self._MAP_SIZE[0] - 1, 2):
                unvisited.add((x, y))

        x = random.randint(0, int((self._MAP_SIZE[0] - 1) // 2)) * 2
        y = random.randint(0, int((self._MAP_SIZE[1] - 1) // 2)) * 2
        frontier = {}
        while unvisited:
            for offset in self._TILE_OFFSETS:
                neighbor = (x + offset[0] * 2, y + offset[1] * 2)
                if not frontier.get(neighbor) and neighbor in unvisited:
                    frontier[neighbor] = (x, y)
            (x, y), parent = random.choice(tuple(frontier.items()))
            self._map[y][x] = 0
            # removal of wall
            self._map[int((y + parent[1]) / 2)][int((x + parent[0]) / 2)] = 0
            frontier.pop((x, y))
            unvisited.remove((x, y))

    def _clear(self: Self) -> None:
        for y in range(self._MAP_SIZE[1]):
            for x in range(self._MAP_SIZE[0]):
                self._map[y][x] = 0

    def run(self: Self) -> None:
        self._running = 1
        start_time = time.time()

        while self._running:
            delta_time = time.time() - start_time
            start_time = time.time()

            rel_game_speed = delta_time * self._GAME_SPEED

            pos = pg.mouse.get_pos()
            y = int(pos[1] // self._TILE_SIZE)
            x = int(pos[0] // self._TILE_SIZE)

            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self._running = 0
                elif event.type == pg.KEYDOWN:
                    if event.key == pg.K_s:
                        self._start = (x, y)
                    elif event.key == pg.K_e:
                        self._end = (x, y)
                    elif event.key == pg.K_p:
                        start = time.time()
                        self._pathfind()
                        self._solve_time = time.time() - start
                    elif event.key == pg.K_g:
                        self._generate()
                    elif event.key == pg.K_c:
                        self._clear()
                    elif event.key == pg.K_a:
                        self._algorithm = 'A*'
                    elif event.key == pg.K_d:
                        self._algorithm = 'Dijkstra'

            pressed = pg.mouse.get_pressed()
            if pressed[0]:
                self._map[y][x] = 1
            elif pressed[2]:
                self._map[y][x] = 0

            self._screen.fill(self._BLACK)
            # Draw Start and End
            pg.draw.rect(self._screen, self._RED, self._rect(self._start))
            pg.draw.rect(self._screen, self._GREEN, self._rect(self._end))
            # Draw Path
            for node in self._path:
                pg.draw.rect(self._screen, self._BLUE, self._rect(node))
            # Draw Obstacles
            for y, row in enumerate(self._map):
                for x, node in enumerate(row):
                    if node:
                        rect = self._rect((x, y))
                        pg.draw.rect(self._screen, self._GREY, rect)

            text = (
                f'Algorithm: {self._algorithm}\n'
                f'Solve Time: {round(self._solve_time, 5)}'
            )
            rendered = self._font.render(text, 1, self._WHITE)
            self._screen.blit(rendered, (10, 10))

            pg.display.update()

        pg.quit()


if __name__ == '__main__':
    Game().run()

