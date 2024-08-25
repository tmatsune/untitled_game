import pygame as pg, os, math, random, sys 
from pygame.locals import * 
import src.settings as s
import src.utils as utils
import src.anim_manager as anim_manager
import src.tilemap as tilemap
import src.entity as entities
import src.inputs as inputs

'''
CUSTOM_GAME_FRAMEWORK: VERSION 1.0
'''
game_name = 'untitled game'
PI = math.pi 
PI2 = 2*math.pi
PI_2 = math.pi/2
PI3_2 = (3*math.pi)/2
PI_6 = math.pi/6

class App:
    def __init__(self) -> None:
        # ---- VARS
        self.dt = 0 
        self.screenshake = 0 
        self.total_time = 0 
        self.level = None

        self.run_loop = False
        self.left_clicked = False
        self.right_clicked = False

        # ---- TIMER VARS
        self.item_drop_timer = s.ITEM_DROP_TIME
        self.level_time = -1

        # ---- LIST VARS
        self.projectiles = [] 
        self.particles = []
        self.circles = []
        self.circle_particles = [] 
        self.sparks = []
        self.font_particles = [] 

        self.offset = [0,0] 
        self.user_inputs = [False, False, False, False]
        self.edges = [s.inf, s.n_inf, s.inf, s.n_inf]  # x, -x, y, -y

        # ---- HASH VARS 
        self.fonts = {
            'basic': f'{s.FONTS_PATH}basic.ttf',
            'font_0': f'{s.FONTS_PATH}font_0.ttf',
            'font_1': f'{s.FONTS_PATH}font_1.ttf',
        }

        # ---- CLASSES 
        self.tile_map = tilemap.TileMap(self)
        self.anim_manager = anim_manager.AnimationManager(f'{s.ANIM_PATH}')
        self.inputs = inputs.Inputs(self)
        self.mouse = inputs.Mouse(self)
        
        # ---- ENTITIES    
        self.player = None
        self.entities = [] 

    def reset(self):
        self.particles = []
        self.projectiles = [] 
        self.circles = []
        self.circle_particles = [] 
        self.offset = [0,0] 
        self.user_inputs = [False, False, False, False]
        self.inputs = inputs.Inputs(self)
        self.edges = [s.inf, s.n_inf, s.inf, s.n_inf] 
        self.dt = 0
        self.screenshake = 0
        self.total_time = 0
        self.entities = []
        self.tile_map.reset_map()

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
        self.player = entities.Player(self, player_starting_pos, [12,12], 'player', True)

# ---- INIT PG
pg.init()
screen: pg.display = pg.display.set_mode((s.SCREEN_WIDTH, s.SCREEN_HEIGHT))
display: pg.Surface = pg.Surface((s.WIDTH, s.HEIGHT))
clock: pg.time = pg.time.Clock()
bg_images = []
for bg in os.listdir(s.BG_PATH):
    bg_images.append(utils.get_image(s.BG_PATH + bg, [s.WIDTH, s.HEIGHT]))
        
app = App()
tile_map = tilemap.TileMap(app)

global enemy_types 
enemy_types = {
    'ground': ['ground_enemy_0', 'ground_enemy_1', 'ground_enemy_2',],
    'flying': ['flying_enemy_0', 'flying_enemy_1', 'flying_enemy_2',],
}


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
    # INIT DATA 
    app.load_level(all_maps[0])
    app.run_loop = True

    app.entities.append(entities.Enemy(app, [190,10], [16,16], 'ground_enemy_0', True))

    while app.run_loop:
        # --- UPDATE/INPUTS
        run()

        # ------- BACKGROUND DATA ----- # 
        
        display.blit(bg_images[0], (0,0))

        # TODO CLOUDS

        # ---------- UPDATE ----------- #
        app.total_time += 1

        # --- inputs 
        app.inputs.handle_inputs()
        app.mouse.handle_click()

        # ---- SPAWN ITEMS/ENTITIES
        # TODO SPAWN ITEMS 
        # TODO SPAWN ENTITIES
        # TODO LEVEL MANAGEMENT 

        # ---- SCROLL OFFSET 



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




        # -------- RENDER TILES / PLAYER ------- # 



        layers = app.tile_map.get_visible_tiles(app.offset)
        for key, layer in layers.items():
            for tile in layer:
                real_pos = [tile[0][0] * s.CELL_SIZE, tile[0][1] * s.CELL_SIZE]
                display.blit(tile[-1], (real_pos[0] - app.offset[0], real_pos[1] - app.offset[1]))



        # ---- PLAYER 



        app.player.update()
        app.player.render(display, app.offset)



        # --------- HANDLE ITEMS -------- #



            # TODO ITEM COLLISIONS
            # TODO ITEM FROM PLAYER DIST 



        # --------- RENDER / UPDATE ENTITIES ------- # 




        for entity in app.entities.copy():
            entity.update()
            entity.render(display, app.offset)
            
            # TODO AI / COLLISIONS FOR ENTITIES



        # --------- HANDLE SHIELDS -------- #



            # TODO RENDER SHIELDS IF PLAYER HAS 



        # --------- HANDLE DRONES -------- #




            # TODO RENDER DRONES IF PLAYER HAS




        # --------- RENDER/UPDATE PROJECTILES -------- #
        


        # [  pos, vel, proj_type, from, image  ]
        remove_list = []
        for i, proj in enumerate(app.projectiles):
            proj[0][0] += proj[1][0]
            proj[0][1] += proj[1][1]

            if proj[3] == 'player':
                pass
                #for entity in app.entities:
                
            if proj[2] in {'player_attack_1'}:
                pg.draw.rect(display, (230, 230, 0), (proj[0][0] - app.offset[0], proj[0][1] - app.offset[1], 1,1))
                player_attack_rect = pg.Rect([proj[0][0], proj[0][1], 1, 1])
                for entity in app.entities:
                    entity_rect: pg.Rect = entity.rect()
                    if entity_rect.colliderect(player_attack_rect):
                        for i in range(3):
                            ang = 0 if proj[1][0] < 0 else math.pi
                            ang += random.uniform(-PI_6, PI_6)
                            hit_spark = utils.add_hit_spark(proj[0], ang)
                            app.sparks.append(hit_spark)
                        entity.take_damage(app.player.attack_1_damage, -1 if proj[1][0] < 0 else 1)

                        app.font_particles.append([proj[0].copy(), [0, -1], 'basic', str(app.player.attack_1_damage), 6, s.WHITE, 1.4, .92])
                        remove_list.append(proj)


            if proj[4]:
                display.blit(proj[4], (proj[0][0] - app.offset[0], proj[0][1] - app.offset[1]))

            if proj[0][0] - app.offset[0] < 0 or proj[0][0] - app.offset[0] > s.WIDTH:
                remove_list.append(proj)

        remove_list.sort()
        for proj in remove_list:
            app.projectiles.remove(proj)




        # --------- RENDER/UPDATE PARTICLES -------- #
        
        # ---- CIRCLES 
        # ---- CIRCLE PARTICLES 

        # ---- SPARKS
        # [ pos, angle, speed, width, width_decay, speed_decay, length, length_decay, color ]
        for spark in app.sparks.copy():
            spark[0][0] += math.cos(spark[1]) * spark[2]
            spark[0][1] += math.sin(spark[1]) * spark[2]
            spark[3] -= spark[4] # sub width by decay 
            spark[2] *= spark[5] # decrase speed by speed decay 
            spark[6] *= spark[7] # decrease lenght by mult of lngth decay 

            if spark[3] <= 0:
                app.sparks.remove(spark)
                continue
            points = [
                (spark[0][0] + math.cos(spark[1]) * spark[6], spark[0][1] + math.sin(spark[1]) * spark[6]),
                (spark[0][0] + math.cos(spark[1] + math.pi / 2) * spark[3], spark[0][1] + math.sin(spark[1] + math.pi / 2) * spark[3]),
                (spark[0][0] - math.cos(spark[1]) * spark[6], spark[0][1] - math.sin(spark[1]) * spark[6]),
                (spark[0][0] + math.cos(spark[1] - math.pi / 2) * spark[3], spark[0][1] + math.sin(spark[1] - math.pi / 2) * spark[3]),
            ]
            points = [(p[0] - app.offset[0], p[1] - app.offset[1]) for p in points]
            color = spark[8] if spark[8] else (247, 180, 0)
            pg.draw.polygon(display, color, points)

        # ---- RENDER FONT PARTICLES



        # [ pos, vel, type, text, size, color, speed, speed_decay ]
        for part in app.font_particles.copy():
            part[0][0] += part[1][0] * part[6]
            part[0][1] += part[1][1] * part[6]
        
            part[6] *= part[7]

            part_text = utils.text_surface_1(f'{part[3]}', part[4], False, part[5], font_path=app.fonts[part[2]])
            display.blit(part_text, (part[0][0] - app.offset[0], part[0][1] - app.offset[1]))

            if part[6] < .1:
                app.font_particles.remove(part)
                
            

        # ---- PARTICLES



        # --------------- GUI ------------- #
            # TODO ADD HEALTHBAR, CURRENT ITEM 

        #load_map_text = utils.text_surface_1(f'load map', 6, False, s.WHITE, font_path=app.fonts['font_0'])
        #display.blit(load_map_text, (s.SCREEN_CENTER[0] - load_map_text.get_width()//2, 40))

        # ------ BLIT SCREENS ------ #

        screenshake_offset = [0,0]
        if app.screenshake > 0:
            app.screenshake -= 1
            screenshake_offset[0] = random.randrange(-8, 8)
            screenshake_offset[1] = random.randrange(-8, 8)

        screen.blit(pg.transform.scale(display, screen.get_size()),(0 + screenshake_offset[0], 0 + screenshake_offset[1]))
        pg.display.flip()
        pg.display.update()

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
                app.user_inputs[0] = True
            if e.key == pg.K_d:
                app.user_inputs[1] = True
            if e.key == pg.K_w:
                app.user_inputs[2] = True
            if e.key == pg.K_s:
                app.user_inputs[3] = True
        if e.type == pg.KEYUP:
            if e.key == pg.K_a:
                app.user_inputs[0] = False
            if e.key == pg.K_d:
                app.user_inputs[1] = False
            if e.key == pg.K_w:
                app.user_inputs[2] = False
            if e.key == pg.K_s:
                app.user_inputs[3] = False

        if e.type == pg.MOUSEBUTTONDOWN:
            if e.button == 1:
                app.left_clicked = True
            if e.button == 3:
                app.right_clicked = True
        if e.type == pg.MOUSEBUTTONUP:
            if e.button == 1:
                app.left_clicked = False
            if e.button == 3:
                app.right_clicked = False


def run():
    update()
    check_inputs()

if __name__ == '__main__':
    main_game_loop()
