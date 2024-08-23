import pygame as pg, sys, os 
import src.mouse as m
import src.settings as s
import src.utils as utils 
import src.tilemap as tilemap


class Level_Editor:
    def __init__(self) -> None:
        pg.init()
        # ------ PG DATA ------ #
        self.screen: pg.display = pg.display.set_mode((s.SCREEN_WIDTH, s.SCREEN_HEIGHT))
        self.display: pg.Surface = pg.Surface((s.WIDTH, s.HEIGHT))
        self.dt: float = 0
        self.clock: pg.time = pg.time.Clock()

        # ------- LIST DATA ------ #
        self.inputs = [False, False, False, False]
        self.offset = [0, 0]
        # ------- HASH DATA ------- # 
        self.fonts = {
            'basic': f'{s.FONTS_PATH}basic.ttf'
        }
        self.windows = {
            'menu': False,
            'save_map': False,
            'load_map': False
        }
        self.active_text_box = {
            'save_map': False,
            'load_map': False
        }

        # ------ VARS ------ #
        self.left_clicked = False
        self.right_clicked = False
        self.curr_map = None
        self.layer = 0
        self.text = []
        self.typing_mode = True

        # ----- CLASSES ----- #
        self.mouse = m.Mouse(self)
        pg.mouse.set_visible(False)
        self.tile_editor = tilemap.Tile_Editor(self)

        # ------ CURR TILE ----- #
        self.tile_type = 0 
        self.tile_name = 0
        self.tile_id= 0
        self.curr_tile = None

    def render(self):

        # --------- UPDATE ---------- #

        self.display.fill((0, 0, 0))
        self.offset[0] += (self.inputs[1] - self.inputs[0]) * s.CELL_SIZE
        self.offset[1] += (self.inputs[3] - self.inputs[2]) * s.CELL_SIZE

        # ----- MOUSE
        mouse_pos = pg.mouse.get_pos()
        self.mouse.pos = [mouse_pos[0]//2, mouse_pos[1]//2]
        self.mouse.update()
        mouse_rect = self.mouse.rect()


        # --------- HANDLE CURR TILE ---------- #


        if self.tile_type >= 0:
            self.tile_type %= len(self.tile_editor.tile_data)

            if self.tile_name >= 0:
                self.tile_name %= len(self.tile_editor.tile_data[self.tile_type])
            elif self.tile_name < 0:
                self.tile_name = len(self.tile_editor.tile_data[self.tile_type]) - 1

            if self.curr_tile and self.tile_editor.tile_data[self.tile_type][0][0] in {'tileset', 'bg_tiles', 'decor'}:
                if self.tile_id >= 0:
                    self.tile_id %= len(self.tile_editor.tile_data[self.tile_type][self.tile_name][2])
                elif self.tile_id < 0:
                    self.tile_id = len(self.tile_editor.tile_data[self.tile_type][self.tile_name][2]) - 1

        elif self.tile_type < 0:
            self.tile_type = len(self.tile_editor.tile_data) - 1

        ui_data = {
            'tile_type': "NONE",
            'tile_name': "NONE",
            'tile_id': "NONE"
        }

        if self.tile_editor.tile_data[self.tile_type][0][0] in {'tileset', 'bg_tiles', 'decor'}:
            tile_type = self.tile_editor.tile_data[self.tile_type][0][0]
            tile_name = self.tile_editor.tile_data[self.tile_type][self.tile_name][1]
            ui_data['tile_type'] = tile_type
            ui_data['tile_name'] = tile_name
            tile_path = self.tile_editor.tile_data[self.tile_type][self.tile_name][2][self.tile_id]
            tile_png = self.tile_editor.tile_data[self.tile_type][self.tile_name][2][self.tile_id].split('/')[-1]
            tile_id = tile_png.split('.')[0]
            ui_data['tile_id'] = tile_id
            tile_config = self.tile_editor.tile_data[self.tile_type][self.tile_name][3][tile_id]

            tile_image = utils.get_image(tile_path, tile_config['size'])
            self.curr_tile = [tile_type, tile_name, tile_id, tile_path, tile_config, tile_image]

        elif self.tile_editor.tile_data[self.tile_type][0][0] == 'markers':
            tile_type = self.tile_editor.tile_data[self.tile_type][0][0]
            marker_name = self.tile_editor.tile_data[self.tile_type][self.tile_name][1]
            ui_data['tile_type'] = tile_type
            ui_data['tile_name'] = marker_name

            tile_path = self.tile_editor.tile_data[self.tile_type][self.tile_name][2]
            tile_image = utils.get_image(tile_path, [s.CELL_SIZE, s.CELL_SIZE])
            self.curr_tile = [tile_type, marker_name, None, tile_path, None, tile_image]

        # --------- MAIN RENDER FUNS ------- # 



        self.tile_editor.test_render(self.display, self.offset)

        if self.curr_tile and not self.typing_mode:
            self.display.blit(self.curr_tile[-1], (self.mouse.pos[0], self.mouse.pos[1]))
            tile_pos = [(self.mouse.pos[0]) // s.CELL_SIZE,(self.mouse.pos[1]) // s.CELL_SIZE]
            pg.draw.rect(self.display, s.WHITE, (tile_pos[0]*s.CELL_SIZE, tile_pos[1]*s.CELL_SIZE, s.CELL_SIZE, s.CELL_SIZE ), 1)
        else:
            self.mouse.render(self.display)

        # --------- ADDING/REMOVING TILES --------- #



        tile_pos = [(self.mouse.pos[0] + self.offset[0]) // s.CELL_SIZE, (self.mouse.pos[1] + self.offset[1]) // s.CELL_SIZE]
        if (self.mouse.left_click == m.Click.JUST_PRESSED or self.mouse.left_click == m.Click.PRESSED) and not self.typing_mode:
            self.tile_editor.add_tile(tile_pos, self.curr_tile, self.layer)
        if (self.mouse.right_click == m.Click.JUST_PRESSED or self.right_clicked == m.Click.PRESSED) and not self.typing_mode:
            self.tile_editor.remove_tile(tile_pos, self.layer)




        # --------- UI --------- #

       

        # ---- TEXT 

        tile_type = ui_data['tile_type']
        tile_name = ui_data['tile_name']
        tile_id = ui_data['tile_id']

        tile_type_text = utils.text_surface_1(f'Type: {tile_type}', 10, False, s.WHITE, font_path=self.fonts['basic'])
        self.display.blit(tile_type_text, [s.WIDTH - tile_type_text.get_width() - 8, 5])

        tile_name_text = utils.text_surface_1(f'Name: {tile_name}', 10, False, s.WHITE, font_path=self.fonts['basic'])
        self.display.blit(tile_name_text, [s.WIDTH - tile_name_text.get_width() - 8, 20])

        tile_id_text = utils.text_surface_1(f'ID: {tile_id}', 10, False, s.WHITE, font_path=self.fonts['basic'])
        self.display.blit(tile_id_text, [s.WIDTH - tile_id_text.get_width() - 8, 35])

        layer_text = utils.text_surface_1(f'Layer: {self.layer}', 10, False, s.WHITE, font_path=self.fonts['basic'])
        self.display.blit(layer_text, [10, 20])

        top_left_pos_text = utils.text_surface_1(f'{self.offset[0]//s.CELL_SIZE},{self.offset[1]//s.CELL_SIZE}', 10, False, s.WHITE, font_path=self.fonts['basic'])
        self.display.blit(top_left_pos_text, [8, 5])

        typing_mode_text = utils.text_surface_1(f'Mode: {self.typing_mode}', 10, False, s.WHITE, font_path=self.fonts['basic'])
        self.display.blit(typing_mode_text, (s.WIDTH - typing_mode_text.get_width() - 5, s.HEIGHT - typing_mode_text.get_height() - 5))


        # ---- MENU 

        menu_button = False
        if self.typing_mode: menu_button = self.button(self.display, [0,s.HEIGHT-20], 'menu', mouse_rect, self.mouse.left_click)
        if menu_button and self.typing_mode:
            if self.windows['menu']: 
                for window in self.windows: self.windows[window] = False
            else: self.windows['menu'] = True

        if self.windows['menu']:
            pg.draw.rect(self.display, (160,160,160), ((s.WIDTH-200)//2, (s.HEIGHT-200)//2, 200, 200))

            show_save_map_button = self.button(self.display, [s.WIDTH//2 - 36,50], 'save map', mouse_rect, self.mouse.left_click)
            show_load_map_button = self.button(self.display, [s.WIDTH//2 - 36,80], 'load_map', mouse_rect, self.mouse.left_click)
            
            if show_save_map_button:
                self.open_window('save_map')
            elif show_load_map_button:
                self.open_window('load_map')
            self.mouse.render(self.display)

        elif self.windows['save_map']:
            pg.draw.rect(self.display, (160,160,160), ((s.WIDTH-200)//2, (s.HEIGHT-200)//2, 200, 200))
            map_name = ''
            for chr in self.text: map_name += chr
            self.text_box(self.display, [s.WIDTH//2 - 36, 80], map_name)
            save_map_button = self.button(self.display, [s.WIDTH//2 - 36,100], 'save map', mouse_rect, self.mouse.left_click)
            if save_map_button:
                self.save_map()
            self.mouse.render(self.display)

        elif self.windows['load_map']:
            pg.draw.rect(self.display, (160,160,160), ((s.WIDTH-200)//2, (s.HEIGHT-200)//2, 200, 200))
            load_map_text = utils.text_surface_1(f'load map', 12, False, s.WHITE, font_path=self.fonts['basic'])
            self.display.blit(load_map_text, (s.SCREEN_CENTER[0] - load_map_text.get_width()//2, 40))

            map_names = os.listdir(s.MAP_PATH)
            for i in range(len(map_names)):
                map_name = map_names[i]
                map_button = self.button(self.display, [s.WIDTH//2 - 36, 50 + i * 30], map_name, mouse_rect, self.mouse.left_click)
                if map_button:
                    self.load_map(map_name)
                    self.close_menu()
            self.mouse.render(self.display)



        # ----- BLIT SCREENS ----- #
        self.screen.blit(pg.transform.scale(self.display, self.screen.get_size()), (0, 0))
        pg.display.flip()
        pg.display.update()



    
    def save_map(self):
        map_name = ''
        for chr in self.text: map_name += chr
        self.tile_editor.save_map(map_name)

    def load_map(self, map_name):
        self.tile_editor.load_map(map_name)

    def close_menu(self): 
        for window in self.windows: self.windows[window] = False
    
    def open_window(self, window_name):
        for window in self.windows: self.windows[window] = False
        if window_name in self.windows: self.windows[window_name] = True
        else:
            assert 0, "ERR: WINDOW NAME NOT IN WINDOWS"

    def text_box(self, surf, pos,text, width=0):
        text_surf = utils.text_surface_1(f'{text}', 10, False, s.BLACK, font_path=self.fonts['basic'])
        size = [text_surf.get_width() * 1.5, text_surf.get_height() * 1.5] if len(text) > 6 else [50,15]
        pg.draw.rect(surf, s.WHITE, (pos[0], pos[1], size[0], size[1]), width)
        surf.blit(text_surf, (pos[0] + text_surf.get_width() * .25, pos[1] + text_surf.get_height() * .25))

    def button(self, surf, pos, text, mouse_rect, left_click, width=1):
        text_surf = utils.text_surface_1(f'{text}', 10, False, s.WHITE, font_path=self.fonts['basic'])

        pg.draw.rect(surf, s.WHITE, (pos[0], pos[1], text_surf.get_width() * 1.5, text_surf.get_height() * 1.5), width)
        surf.blit(text_surf, (pos[0] + text_surf.get_width() * .25, pos[1] + text_surf.get_height() * .25))

        button_rect: pg.rect = pg.Rect([pos[0], pos[1], text_surf.get_width() * 1.5, text_surf.get_height() * 1.5 ])
        if button_rect.colliderect(mouse_rect) and left_click == m.Click.JUST_PRESSED:
            return True
        return False

    def check_inputs(self):
        for e in pg.event.get():
            if e.type == pg.QUIT:
                pg.quit()
                sys.exit()
            if e.type == pg.KEYDOWN:
                if self.typing_mode:
                    key = pg.key.name(e.key)
                    if key == 'return':
                        if self.windows['save_map']:
                            self.save_map()
                    elif key == 'space':
                        print('space')
                    elif key == 'backspace':
                        if len(self.text) > 0: self.text.pop()
                        else: print('no text')
                    elif key == 'tab':
                        self.typing_mode = False
                        self.text = [] 
                    elif key == '-':
                        self.text.append('_')
                    else:
                        self.text.append(key)
                    return 
                
                if e.key == pg.K_ESCAPE:
                    pg.quit()
                    sys.exit()
                if e.key == pg.K_TAB:
                    self.typing_mode = True
                if e.key == pg.K_f:
                    if self.curr_tile:
                        tile_imgs = self.tile_editor.tile_data[self.tile_type][self.tile_name][2]
                        tile_pos = [(self.mouse.pos[0] + self.offset[0]) // s.CELL_SIZE,
                                    (self.mouse.pos[1] + self.offset[1]) // s.CELL_SIZE]
                        self.tile_editor.auto_tile(tile_pos, tile_imgs, self.layer)

                if e.key == pg.K_q:
                    self.tile_type -= 1
                    self.tile_name = 0 
                    self.tile_id = 0 
                if e.key == pg.K_e:
                    self.tile_type += 1
                    self.tile_name = 0
                    self.tile_id = 0
                if e.key == pg.K_a:
                    self.tile_name -= 1 
                if e.key == pg.K_d:
                    self.tile_name += 1

                if e.key == pg.K_w:
                    self.tile_id += 1
                if e.key == pg.K_s:
                    self.tile_id -= 1

                if e.key == pg.K_COMMA:
                    self.layer -= 1
                if e.key == pg.K_PERIOD:
                    self.layer += 1

                if e.key == pg.K_LEFT:
                    self.inputs[0] = True
                if e.key == pg.K_RIGHT:
                    self.inputs[1] = True 
                if e.key == pg.K_UP:
                    self.inputs[2] = True
                if e.key == pg.K_DOWN:
                    self.inputs[3] = True

            if e.type == pg.KEYUP:
                if e.key == pg.K_LEFT:
                    self.inputs[0] = False
                if e.key == pg.K_RIGHT:
                    self.inputs[1] = False
                if e.key == pg.K_UP:
                    self.inputs[2] = False
                if e.key == pg.K_DOWN:
                    self.inputs[3] = False
    

            if e.type == pg.MOUSEBUTTONDOWN:
                if e.button == 1:
                    self.left_clicked = True
                if e.button == 3:
                    self.right_clicked = True
            if e.type == pg.MOUSEBUTTONUP:
                if e.button == 1:
                    self.left_clicked = False
                if e.button == 3:
                    self.right_clicked = False

    def update(self):
        self.clock.tick(s.FPS)
        pg.display.set_caption(f'{self.clock.get_fps()}')
        self.dt = self.clock.tick(s.FPS)
        self.dt /= 1000

    def run(self):
        while True:
            self.render()
            self.update()
            self.check_inputs()

if __name__ == '__main__':
    app = Level_Editor()
    app.run()
