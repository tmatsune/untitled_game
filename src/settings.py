import pygame as pg
import math, random

# ------ CONST 
SCREEN_WIDTH = 640
SCREEN_HEIGHT = 512
WIDTH = SCREEN_WIDTH // 2
HEIGHT = SCREEN_HEIGHT // 2
SCREEN_CENTER = [WIDTH//2, HEIGHT//2]
FPS = 60
CELL_SIZE = 16
COLS = WIDTH // CELL_SIZE
ROWS = HEIGHT // CELL_SIZE
GRAVITY = 1
inf = float('inf')
n_inf = float('-inf')

# ------ DEFAULT ENTITY
DEFAULT_SPEED = 4
DEFAULT_JUMPS = 2
DEFAULT_JUMP_SCALE = -12

# ------ COLORS 
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
SKY_BLUE = (70, 210, 255)
TEST_COLOR = (70,120,140)

# ------ PATHS 
# IMAGES
IMAGES_PATH = 'src/images/'
ANIM_PATH = f'{IMAGES_PATH}animations/'
IMAGES_IMAGES_PATH = f'{IMAGES_PATH}images/'

#TILES
TILES_PATH = 'src/tiles/'
TILESET_PATH = f'{TILES_PATH}tileset/'
BG_TILES_PATH = f'{TILES_PATH}bg_tiles/'
OBJECTS_PATH = f'{TILES_PATH}objects/'
MARKERS_PATH = f'{TILES_PATH}markers/'
DECOR_PATH = f'{TILES_PATH}decor/'

#OTHER 
FONTS_PATH = 'src/fonts/'
MAP_PATH = 'src/maps/'
SOUND_PATH = 'src/sound/'
