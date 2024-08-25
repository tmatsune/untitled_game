import pygame as pg, math 
import src.settings as s
import src.utils as utils

class Entity:
    def __init__(self, app, pos, size, type, animated=None) -> None:
        self.app = app 

        # ---- LIST VARS
        self.vel = [0,0]
        self.pos = pos.copy()
        self.size = size.copy()
        self.scale = [1,1]

        # ----- VARS
        self.type = type 
        self.speed = s.DEFAULT_SPEED
        self.gravity = s.GRAVITY
        self.max_health = s.DEFAULT_MAX_HEALTH
        self.health = self.max_health
        self.reset_hurt_time = s.DEFAULT_HURT_TIME
        self.hurt_time = self.reset_hurt_time

        self.knock_back = [1,0]

        # ---- VAR BOOLS
        self.flip = False
        self.hurt = False
        self.animated = animated

        if animated:
            self.state = 'idle'
            self.animation_data = app.anim_manager.get_anim_data(type)
            self.anim = self.animation_data.animations[self.state].copy()

    def update(self):
        self.hurt_timer()
        self.anim.update(self.app.dt)

    def render(self, surf, offset=[0,0]):
        offset = offset.copy()
        if self.anim.config['offset']:
            offset[0] += self.anim.config['offset'][0]
            offset[1] += self.anim.config['offset'][1]
        image = self.anim.image()
        if self.scale != [1, 1]:
            image = pg.transform.scale(image, (int(self.scale[0] * self.anim.config['size'][0]), int(self.scale[1] * self.anim.config['size'][1])))
            x_diff = (s.self.anim.config['size'][0] - image.get_width()) // 2
            y_diff = (s.self.anim.config['size'][0] - image.get_height())
            offset[0] -= x_diff
            offset[1] -= y_diff

        if self.flip:
            image = pg.transform.flip(image, self.flip, False)

        if not self.hurt:
            surf.blit(image, (self.pos[0] - offset[0], self.pos[1] - offset[1]))
        else:
            if math.sin(self.app.total_time) > 0:
                sil = utils.silhouette(image)
                surf.blit(
                    sil, (self.pos[0] - offset[0], self.pos[1] - offset[1]))

        #pg.draw.rect(surf, (255,120,0), (self.pos[0] - offset[0], self.pos[1] - offset[1], self.size[0], self.size[1]), 1) # TEST
        #pg.draw.circle(surf, (255, 0, 0), (self.center()[0] - offset[0], self.center()[1] - offset[1]), 1)             # TEST

    def hurt_timer(self):
        if self.hurt:
            self.hurt_time -= 1 
            if self.hurt_time < 0:
                self.hurt = False
                self.hurt_time = self.reset_hurt_time

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

    def state_handler(self, collisions):
        if self.state == 'idle':
            if self.vel[0] != 0:
                if not collisions['down']: self.change_state('jump')
                else: self.change_state('run')
            elif not collisions['down']:
                self.change_state('jump')
        elif self.state == 'run':
            if self.vel[0] == 0:
                self.change_state('idle')
            elif not collisions['down']:
                self.change_state('jump')
        elif self.state == 'jump':
            if collisions['down']:
                self.change_state('idle')

    def take_damage(self, amount, direct):
        self.health -= amount
        self.hurt = True
        self.knock_back = [1.5, direct]
    
class Player(Entity):
    def __init__(self, app, pos, size, type, animated=None) -> None:
        super().__init__(app, pos, size, type, animated)
        self.max_health = 100
        self.health = self.max_health
        self.max_jumps = s.DEFAULT_JUMPS
        self.jumps = s.DEFAULT_JUMPS
        self.jump_scale = s.DEFAULT_JUMP_SCALE

        # ATTACK 
        self.attack_1_damage = s.DEFAULT_ATTACK_1
        self.attack_2_damage = s.DEFAULT_ATTACK_2

    # if flip: left 
    def update(self):
        super().update()

        if self.app.user_inputs[1]: self.flip = False
        elif self.app.user_inputs[0]: self.flip = True

        # ---- MOVEMENT 
        if self.app.inputs.input_just_clicked('up'): self.jump()
        self.vel[0] = (self.app.inputs.input_active('right') - self.app.inputs.input_active('left')) * self.speed
        self.vel[1] = min(10, self.vel[1] + 1)

        '''
        nearby_rects = self.app.tile_map.get_nearby_tiles(self.pos)
        collisions = self.movement(self.vel, nearby_rects)
        self.state_handler(collisions)
        if collisions['down']:
            self.vel[1] = 0 
            self.jumps = self.max_jumps
        '''

        # ---- ATTACK 
        if self.app.mouse.left_just_clicked():
            self.attack_1(self.flip)
        elif self.app.mouse.right_just_clicked():
            self.attack_2(self.flip)

    def render(self, surf, offset=[0, 0]):
        nearby_rects = self.app.tile_map.get_nearby_tiles(self.pos)
        collisions = self.movement(self.vel, nearby_rects)
        self.state_handler(collisions)
        if collisions['down']:
            self.vel[1] = 0 
            self.jumps = self.max_jumps
        return super().render(surf, offset)
    
    def attack_1(self, left):
        if left: 
            self.app.projectiles.append([ 
                [self.center()[0]-0, self.center()[1]],
                [-14, 0],
                'player_attack_1',
                self.type,
                None,
            ])
        else: 
            self.app.projectiles.append([
                [self.center()[0]+0, self.center()[1]],
                [14, 0],
                'player_attack_1',
                self.type,
                None,
            ])
            hit_spark = utils.add_shot_spark([self.center()[0]-1, self.center()[1]], 0)
            self.app.sparks.append(hit_spark)

    def attack_2(self, left):
        if left:
            self.app.projectiles.append([
                [self.center()[0]-0, self.center()[1]],
                [0, 0],
                'player_attack_2',
                self.type,
                None,
                left,
            ])
        else:
            self.app.projectiles.append([
                [self.center()[0]+0, self.center()[1]],
                [0, 0],
                'player_attack_2',
                self.type,
                None,
                left
            ])


class Enemy(Entity):
    def __init__(self, app, pos, size, type, animated=None) -> None:
        super().__init__(app, pos, size, type, animated)
        if type == 'ground_enemy_0':
            self.speed = 2
            self.attack_damage = 10    
            self.bar_dim = [0,-2,20,4]

    def update(self):
        super().update()

        self.vel[1] = min(10, self.vel[1] + 1)

        if self.knock_back[0] > 1:
            self.knock_back[0] -= .1 
            if self.vel[0] == 0: self.vel[0] = self.knock_back[1]
            self.vel[0] *= 1 * self.knock_back[0]
        if self.knock_back[0] <= 1:
            self.vel[0] = 0
            self.knock_back[0] = 1

        nearby_rects = self.app.tile_map.get_nearby_tiles(self.pos)
        collisions = self.movement(self.vel, nearby_rects)

        self.state_handler(collisions)
        if collisions['down']:
            self.vel[1] = 0

    def render(self, surf, offset=[0, 0]):
        #pg.draw.rect(surf, s.RED, (self.pos[0] - offset[0], self.pos[1] - offset[1], self.size[0], self.size[1]), 1)
        if self.health < self.max_health:
            pg.draw.rect(surf, s.RED, (self.pos[0] - offset[0], self.pos[1] - offset[1] + self.bar_dim[1], self.bar_dim[2]*(self.health/self.max_health), self.bar_dim[3]))
            pg.draw.rect(surf, s.WHITE, (self.pos[0] - offset[0], self.pos[1] - offset[1] + self.bar_dim[1], self.bar_dim[2], self.bar_dim[3]), 1)
        super().render(surf, offset)



