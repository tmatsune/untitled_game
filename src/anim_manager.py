import pygame as pg, os, json
import src.settings as s
import src.utils as utils

class AnimationData:
    def __init__(self, path, type) -> None:
        self.type = type 
        self.animations_data = {}
        self.animations = {}
        for anim in os.listdir(path):
            self.animations_data[anim] = {'images': [], 'config': None}
            full_path = f'{path}/{anim}/'
            for img in os.listdir(path + '/' + anim):
                if img.split('.')[-1] == 'png':
                    self.animations_data[anim]['images'].append(
                        utils.get_image(full_path+img, [s.CELL_SIZE, s.CELL_SIZE]))
                else:
                    f = open(full_path + img, 'r')
                    config = json.loads(f.read()) 
                    f.close()
                    self.animations_data[anim]['config'] = config
        self.create_animations()

    def create_animations(self):
        for type, data in self.animations_data.items():
            images = data['images']
            config = data['config']
            self.animations[type] = Animation(type, images, config)

class Animation:
    def __init__(self, state, images, config) -> None:
        self.state = state
        self.images = images.copy()
        self.config = config  # config{ frames:[], loop: bool, offset:[] }
        self.time = 0
        self.frame = 0

    def update(self, dt):
        if len(self.images) > 1:
            self.frame %= len(self.images) - 1
            self.time += 1
            if self.time > self.config['frames'][self.frame]:
                self.frame += 1
                self.time = 0
        else:
            self.frame = 0

    def image(self):
        return self.images[self.frame]

    def copy(self):
        return Animation(self.state, self.images, self.config)

class AnimationManager:
    def __init__(self, path) -> None:
        self.animations = {}
        self.path = path 
        self.get_animations(path)

    def get_animations(self, path):
        for anim_type in os.listdir(path):
            anims = os.listdir(path + anim_type)
            if anims:
                self.animations[anim_type] = AnimationData(s.ANIM_PATH + anim_type, anim_type)

    def get_anim_data(self, type):
        if type in self.animations:
            return self.animations[type]
        assert 0, 'type not found, invalid type'