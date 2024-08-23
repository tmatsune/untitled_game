import pygame as pg, os, math, random, sys 
from pygame.locals import * 
import src.settings as s
import src.utils as utils
import src.anim_manager as anim_manager
import src.tilemap as tilemap
import src.entity as entities
import src.mouse as m

'''
CUSTOM_GAME_FRAMEWORK: VERSION 1.0
'''
game_name = 'untitled game'

class App:
    def __init__(self) -> None:
        # ---- VARS
        self.dt = 0 
        self.screenshake = 0 
        self.total_time = 0 
        self.level = None

        # ---- LIST VARS
        self.particles = []
        self.projectiles = [] 
        self.circles = []
        self.circle_particles = [] 
        self.offset = [0,0] 
        self.inputs = [False, False, False, False]
        self.edges = [s.inf, s.n_inf, s.inf, s.n_inf]  # x, -x, y, -y

        # ---- CLASSES 
        self.tile_map = tilemap.TileMap(self)
        self.anim_manager = anim_manager.AnimationManager(f'{s.ANIM_PATH}')
        
        # ---- ENTITIES    
        self.player = None
        self.entities = [] 

    def load_spawn_points(self, level_data):
        pass

    def load_level_data(self, level):
        markers = self.tile_map.load_map(level)
        for pos in self.tile_map.tiles:
            x = pos[0] * s.CELL_SIZE
            y = pos[1] * s.CELL_SIZE
            if x < self.edges[0]: self.edges[0] = x
            if x > self.edges[1]: self.edges[1] = x + s.CELL_SIZE
            if y < self.edges[2]: self.edges[2] = y + s.CELL_SIZE*2
            if y > self.edges[3]: self.edges[3] = y + s.CELL_SIZE*1
        return markers

    def load_level(self, level):
        markers = self.load_level_data(level)
        #markers = self.load_spawn_points(level_data)
        player_starting_pos = [100,100]
        
        for key, data in markers.copy().items():
            if data[1] == 'player_marker.png':
                player_starting_pos = [key[0]*s.CELL_SIZE, key[1]*s.CELL_SIZE]
                del markers[key]
        self.player = entities.Player(self, player_starting_pos, [s.CELL_SIZE, s.CELL_SIZE], 'player', True)

# ---- INIT PG
pg.init()
screen: pg.display = pg.display.set_mode((s.SCREEN_WIDTH, s.SCREEN_HEIGHT))
display: pg.Surface = pg.Surface((s.WIDTH, s.HEIGHT))
clock: pg.time = pg.time.Clock()
        
app = App()
mouse = m.Mouse(app)
tile_map = tilemap.TileMap(app)

all_maps = []
for level in os.listdir(s.MAP_PATH):
    all_maps.append(level[:-5])

# ---- WINDOWS 
def test_game_loop():
    app.load_level(all_maps[0])

    while True:
        # --------- UPDATE --------- #
        run()
        display.fill(s.TEST_COLOR)

        # ------- SCROLL OFFSET ------- #
        app.offset[0] += ((app.player.pos[0] - s.WIDTH // 2) - app.offset[0]) / 12
        app.offset[1] += ((app.player.pos[1] - s.HEIGHT // 2) - app.offset[1]) / 12

        if app.offset[0] < app.edges[0]:
            app.offset[0] = app.edges[0]
        if app.offset[0] + s.WIDTH > app.edges[1]:
            app.offset[0] = app.edges[1] - s.WIDTH

        if app.offset[1] < app.edges[2]:
            app.offset[1] = app.edges[2]
        if app.offset[1] + s.HEIGHT > app.edges[3]:
            app.offset[1] = app.edges[3] - s.HEIGHT

        # -------- RENDER TILES ------- # 

        layers = app.tile_map.get_visible_tiles(app.offset)
        for key, layer in layers.items():
            for tile in layer:
                real_pos = [tile[0][0] * s.CELL_SIZE, tile[0][1] * s.CELL_SIZE]
                display.blit(tile[-1], (real_pos[0] - app.offset[0], real_pos[1] - app.offset[1]))

        # --------- PLAYER --------- #

        app.player.update()
        app.player.render(display, app.offset)

        # ------ BLIT SCREENS ------ #
        screenshake_offset = [0,0]
        if app.screenshake > 0:
            app.screenshake -= 1
            screenshake_offset[0] = random.randrange(-8, 8)
            screenshake_offset[1] = random.randrange(-8, 8)

        screen.blit(pg.transform.scale(display, screen.get_size()),(0 + screenshake_offset[0], 0 + screenshake_offset[1]))
        pg.display.flip()
        pg.display.update()

def menu_loop():
    pass

def main_game_loop():
    pass

# ---- MAIN PG FUNCS
def update():
    clock.tick(s.FPS)
    pg.display.set_caption(game_name)
    app.dt = clock.tick(s.FPS)
    app.dt /= 1000

def check_inputs():
    for e in pg.event.get():
        if e.type == pg.QUIT:
            pg.quit()
            sys.exit()
        if e.type == pg.KEYDOWN:
            if e.key == pg.K_1:
                pg.quit()
                sys.exit()
            if e.key == pg.K_a:
                app.inputs[0] = True
            if e.key == pg.K_d:
                app.inputs[1] = True
            if e.key == pg.K_w:
                app.inputs[2] = True
                if app.player: app.player.jump()
            if e.key == pg.K_s:
                app.inputs[3] = True
        if e.type == pg.KEYUP:
            if e.key == pg.K_a:
                app.inputs[0] = False
            if e.key == pg.K_d:
                app.inputs[1] = False
            if e.key == pg.K_w:
                app.inputs[2] = False
            if e.key == pg.K_s:
                app.inputs[3] = False

def run():
    update()
    check_inputs()

if __name__ == '__main__':
    test_game_loop()
