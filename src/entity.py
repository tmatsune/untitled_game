import pygame as pg 
import src.settings as s

class Entity:
    def __init__(self, app, pos, size, type, animated=None) -> None:
        self.app = app 

        # ----- LIST VARS
        self.vel = [0,0]
        self.pos = pos.copy()
        self.size = size.copy()
        self.scale = [1,1]

        # ----- VARS
        self.type = type 
        self.speed = s.DEFAULT_SPEED
        self.max_jumps = s.DEFAULT_JUMPS
        self.jumps = s.DEFAULT_JUMPS
        self.jump_scale = s.DEFAULT_JUMP_SCALE
        self.flip = False

        self.animated = animated

        if animated:
            self.state = 'idle'
            self.animation_data = app.anim_manager.get_anim_data(type)
            self.anim = self.animation_data.animations[self.state].copy()

    def update(self):
        self.anim.update(self.app.dt)

    def render(self, surf, offset=[0,0]):
        offset = offset.copy()
        if self.anim.config['offset']:
            offset[0] += self.anim.config['offset'][0]
            offset[1] += self.anim.config['offset'][1]
        image = self.anim.image()
        if self.scale != [1, 1]:
            image = pg.transform.scale(image, 
                                     (int(self.scale[0] * self.anim.config['size'][0]), int(self.scale[1] * self.anim.config['size'][1])))
            x_diff = (s.self.anim.config['size'][0] - image.get_width()) // 2
            y_diff = (s.self.anim.config['size'][0] - image.get_height())
            offset[0] -= x_diff
            offset[1] -= y_diff

        if self.flip:
            image = pg.transform.flip(image, self.flip, False)


        pg.draw.rect(surf, (255,0,0), (self.pos[0] - offset[0], self.pos[1] - offset[1], s.CELL_SIZE, s.CELL_SIZE), 1)
        surf.blit(image, (self.pos[0] - offset[0], self.pos[1] - offset[1]))

    def rect(self):
        return pg.Rect(self.pos[0], self.pos[1], self.size[0], self.size[1])

    def center(self):
        return [self.pos[0] + self.size[0] // 2, self.pos[1] + self.size[1] // 2]

    def change_state(self, state):
        if self.state != state:
            self.state = state
            self.anim = self.animation_data.animations[state].copy()

    def movement(self, vel, tiles):
        self.pos[0] += vel[0]
        hitable_tiles = self.get_tile_hits(self.rect(), tiles)
        curr_rect = self.rect()
        directions = {'left': False, 'right': False, 'up': False, 'down': False}

        for tile in hitable_tiles:
            if vel[0] > 0:
                curr_rect.right = tile.left
                self.pos[0] = curr_rect.left
                directions['right'] = True
            elif vel[0] < 0:
                curr_rect.left = tile.right
                self.pos[0] = curr_rect.left
                directions['left'] = True

        self.pos[1] += vel[1]
        hitable_tiles = self.get_tile_hits(self.rect(), tiles)
        curr_rect = self.rect()
        for tile in hitable_tiles:
            if vel[1] > 0:
                curr_rect.bottom = tile.top
                self.pos[1] = curr_rect.y
                directions['down'] = True
            if vel[1] < 0:
                curr_rect.top = tile.bottom
                self.pos[1] = curr_rect.y
                directions['up'] = True
        return directions

    def get_tile_hits(self, rect, tiles):
        hits = []
        for tile in tiles:
            if rect.colliderect(tile):
                hits.append(tile)
        return hits
    
    def jump(self):
        if self.jumps > 0:
            self.vel[1] = self.jump_scale
            self.jumps -= 1
    

class Player(Entity):
    def __init__(self, app, pos, size, type, animated=None) -> None:
        super().__init__(app, pos, size, type, animated)

    def update(self):
        super().update()

        if self.app.inputs[1]: self.flip = False
        elif self.app.inputs[0]: self.flip = True

        self.vel[1] = min(10, self.vel[1] + 1)
        self.vel[0] = (self.app.inputs[1] - self.app.inputs[0]) * self.speed

        nearby_rects = self.app.tile_map.get_nearby_tiles(self.pos)
        collisions = self.movement(self.vel, nearby_rects)
        
        if collisions['down']:
            self.vel[1] = 0 
            self.jumps = self.max_jumps




