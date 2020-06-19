# Visualization of Dijkstra's pathfinding algorithm
import pygame as pg
from os import environ
from sprites import *
from settings import *

environ['SDL_VIDEO_CENTERED'] = '1'


class Dijkstra:
    # main loop class
    def __init__(self):
        pg.init()
        self.screen = pg.display.set_mode((WIDTH, HEIGHT))
        pg.display.set_caption("Dijkstra")
        self.clock = pg.time.Clock()
        self.running = True
        self.start, self.end = None, None
        self.algo_run, self.algo_end = False, False

    def new(self):
        self.all_sprites = pg.sprite.LayeredUpdates()
        self.walls = pg.sprite.Group()
        self.visited, self.path = pg.sprite.Group(), pg.sprite.Group()
        self.graph = Graph(self)

    def run(self):
        while self.running:
            self.clock.tick(FPS)
            self.events()
            self.update()
            self.draw()

    def events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.running = False

            # set start and end fields at the current mouse position
            # when s or e get pressed on keyboard
            # CTRL + R to run simulation, CTRL + C to clear board
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_s:
                    if self.start:
                        self.clear_board()
                        self.graph.distances[self.graph.start[0]][self.graph.start[1]] = float('inf')
                        self.start.kill()
                    self.start = Start(self, *(pg.mouse.get_pos()))
                if event.key == pg.K_e:
                    if self.end:
                        self.clear_board()
                        self.end.kill()
                    self.end = End(self, *(pg.mouse.get_pos()))
                if event.key == pg.K_r and pg.key.get_mods() & pg.KMOD_CTRL:
                    self.algo_run, self.algo_end = True, True
                    self.algo_time = pg.time.get_ticks()
                    self.graph.dijkstra(self.graph.start, self.graph.end)
                if event.key == pg.K_c and pg.key.get_mods() & pg.KMOD_CTRL:
                    self.clear_board()

            # create walls when left mouse button is pressed
            if pg.mouse.get_pressed()[0]:
                Wall(self, *(pg.mouse.get_pos()))

    def update(self):
        self.all_sprites.update()

        # if algorithm is running and enough time has passed
        # run another iteration of Dijkstra's algorithm
        if self.algo_run and pg.time.get_ticks() - self.algo_time > 15:
            self.algo_time = pg.time.get_ticks()
            a = self.graph.dijkstra(self.graph.start, self.graph.end)
            if a is False:
                self.algo_run = False

        # if algorithm has finished, wait a bit then display
        # shortest path
        if self.algo_end and not self.algo_run and pg.time.get_ticks() - self.algo_time - 300 > 500:
            node = (self.end.rect.topleft[1] // 16, self.end.rect.topleft[0] // 16)
            while node != (self.start.rect.topleft[1] // 16, self.start.rect.topleft[0] // 16):
                Shortest(self, node[1], node[0])
                node = self.graph.prev[(node[0], node[1])]

    def draw(self):
        self.screen.fill(GREY)
        self.all_sprites.draw(self.screen)

        # draw the grid
        for i in range(1, 48):
            pg.draw.line(self.screen, WHITE, (i * TILE_SIZE, 0), (i * TILE_SIZE, HEIGHT))
        for j in range(1, 32):
            pg.draw.line(self.screen, WHITE, (0, j * TILE_SIZE), (WIDTH, j * TILE_SIZE))
        
        pg.display.flip()

    def clear_board(self):
        # clear the board and reset all graph properties
        self.algo_end = False
        for sprite in self.visited:
            sprite.kill()
        for sprite in self.path:
            sprite.kill()
        for sprite in self.walls:
            sprite.kill()
        self.graph.distances = [[float('inf')] * 48 for i in range(32)]
        self.graph.prev, self.graph.walls = {}, []
        self.graph.start = (self.start.rect.topleft[1] // 16, self.start.rect.topleft[0] // 16)
        self.graph.pq = [[0, self.graph.start]]
        self.graph.distances[self.graph.start[0]][self.graph.start[1]] = 0


# main loop
g = Dijkstra()
g.new()
while g.running:
    g.run()

pg.quit()
