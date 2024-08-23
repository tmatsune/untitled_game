import pygame as pg 
import math, random 

# ----- IMAGES
def get_image(path: str, scale: list, color=None) -> pg.image:
    img: pg.image = pg.image.load(path)
    img = pg.transform.scale(img, (scale[0], scale[1])).convert_alpha()
    if color: img = img.set_colorkey(color)
    return img

def load_img(path):
    img = pg.image.load(path)
    return img

def scale_image(img, scale):
    return pg.transform.scale(img, (scale[0], scale[1]))

def color_swap_image(img, old_color, color):
    img = img.copy() 
    img.set_colorkey(old_color)  
    pixel_array = pg.PixelArray(img)
    pixel_array.replace(old_color, color)
    img = pixel_array.surface
    return img

def swap_color(img, old_c, new_c):
    global e_colorkey
    img.set_colorkey(old_c)
    surf = img.copy()
    surf.fill(new_c)
    surf.blit(img, (0, 0))
    return surf

def silhouette(surf, color=(255, 255, 255)):
    mask = pg.mask.from_surface(surf)
    new_surf = swap_color(mask.to_surface(), (255, 255, 255), color)
    new_surf.set_colorkey((0, 0, 0))
    return new_surf

# ----- TEXT 
def text_surface(text: str, size: int, italic: bool, rgb: tuple, font='arial', bold=True):
    font = pg.font.SysFont(font, size, bold, italic)
    text_surface = font.render(text, False, rgb)
    return text_surface

def text_surface_1(text: str, size: int, italic: bool, rgb: tuple, font_path=None, bold=True):
    if font_path: font = pg.font.Font(font_path, size) 
    else: font = pg.font.SysFont('arial', size, bold, italic)  
    if bold: font.set_bold(True)
    if italic: font.set_italic(True)
    text_surface = font.render(text, False, rgb)
    return text_surface

def render_text_box(surf, pos: list, size: list[int], color: tuple, hollow: int = 0):
    pg.draw.rect(surf, color, (pos[0], pos[1], size[0], size[1]), hollow)

# ----- OTHER 
def distance(a, b):
    return math.sqrt(math.pow(abs(a[0] - b[0]), 2) + math.pow(a[1] - b[1], 2))

def mask_collision(mask1, a: list, mask2, b: list): return mask2.overlap(
    mask1, (a[0] - b[0], a[1] - b[1]))
