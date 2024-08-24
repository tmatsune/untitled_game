import pygame as pg
from enum import Enum
from .settings import CELL_SIZE, RED

false = False
true = True

class Click(Enum):
    NONE = 0
    JUST_PRESSED = 1
    PRESSED = 2
    JUST_RELEASED = 3

class Mouse:
    def __init__(self, app) -> None:
        self.app = app
        self.left_click = Click.NONE
        self.right_click = Click.NONE
        self.pos = [0, 0]
        self.tile_pos = [0, 0]
        self.mouse_rect = pg.Rect(0, 0, 3, 3)

    def update(self):
        self.tile_pos = [self.pos[0] // CELL_SIZE, self.pos[1] // CELL_SIZE]
        self.handle_click()
        self.mouse_rect = pg.Rect(self.pos[0], self.pos[1], 3, 3)

    def right_acitve(self): return self.right_click == Click.JUST_PRESSED or self.right_click == Click.PRESSED
    def left_active(self): return self.left_click == Click.JUST_PRESSED or self.left_click == Click.PRESSED
    def right_just_clicked(self): return self.right_click == Click.JUST_PRESSED
    def left_just_clicked(self): return self.left_click == Click.JUST_PRESSED

    def handle_click(self):
        # ---- LEFT CLICK ---- #
        if self.app.left_clicked and self.left_click == Click.JUST_PRESSED:
            self.left_click = Click.PRESSED
        if self.app.left_clicked and self.left_click == Click.NONE:
            self.left_click = Click.JUST_PRESSED
        if not self.app.left_clicked:
            if (self.left_click == Click.PRESSED or self.left_click == Click.JUST_PRESSED):
                self.left_click = Click.JUST_RELEASED
            elif self.left_click == Click.JUST_RELEASED:
                self.left_click = Click.NONE
        # ---- RIGHT CLICK ---- #
        if self.app.right_clicked and self.right_click == Click.JUST_PRESSED:
            self.right_click = Click.PRESSED
        if self.app.right_clicked and self.right_click == Click.NONE:
            self.right_click = Click.JUST_PRESSED
        if not self.app.right_clicked:
            if (self.right_click == Click.PRESSED or self.right_click == Click.JUST_PRESSED):
                self.right_click = Click.JUST_RELEASED
            elif self.right_click == Click.JUST_RELEASED:
                self.right_click = Click.NONE

    def render(self, surf):
        pg.draw.rect(surf, RED, (self.pos[0], self.pos[1], 3, 3))

    def rect(self) -> pg.Rect:
        return self.mouse_rect

class Inputs:
    def __init__(self, app) -> None:
        self.app = app 
        self.left = Click.NONE
        self.right = Click.NONE
        self.up = Click.NONE
        self.down = Click.NONE 

    def input_active(self, input):
        if input == 'left': return self.left == Click.JUST_PRESSED or self.left == Click.PRESSED
        elif input == 'right': return self.right == Click.JUST_PRESSED or self.right == Click.PRESSED
        elif input == 'up': return self.up == Click.JUST_PRESSED or self.up == Click.PRESSED
        elif input == 'down': return self.down == Click.JUST_PRESSED or self.down == Click.PRESSED
    
    def input_just_clicked(self, input):
        if input == 'left': return self.left == Click.JUST_PRESSED 
        elif input == 'right': return self.right == Click.JUST_PRESSED
        elif input == 'up': return self.up == Click.JUST_PRESSED
        elif input == 'down': return self.down == Click.JUST_PRESSED

    def handle_inputs(self):
        # LEFT 
        if self.app.inputs.input_active and self.left == Click.JUST_PRESSED: self.left = Click.PRESSED
        if self.app.user_inputs[0] and self.left == Click.NONE: self.left = Click.JUST_PRESSED
        if not self.app.user_inputs[0]:
            if (self.left == Click.PRESSED or self.left == Click.JUST_PRESSED): self.left = Click.JUST_RELEASED
            elif self.left == Click.JUST_RELEASED: self.left = Click.NONE

        # RIGHT 
        if self.app.user_inputs[1] and self.right == Click.JUST_PRESSED: self.right = Click.PRESSED
        if self.app.user_inputs[1] and self.right == Click.NONE: self.right = Click.JUST_PRESSED
        if not self.app.user_inputs[1]:
            if (self.right == Click.PRESSED or self.right == Click.JUST_PRESSED): self.right = Click.JUST_RELEASED
            elif self.right == Click.JUST_RELEASED: self.right = Click.NONE

        # UP 
        if self.app.user_inputs[2] and self.up == Click.JUST_PRESSED: self.up = Click.PRESSED
        if self.app.user_inputs[2] and self.up == Click.NONE: self.up = Click.JUST_PRESSED
        if not self.app.user_inputs[2]:
            if (self.up == Click.PRESSED or self.up == Click.JUST_PRESSED): self.up = Click.JUST_RELEASED
            elif self.up == Click.JUST_RELEASED: self.up = Click.NONE

        # DOWN 
        if self.app.user_inputs[3] and self.down == Click.JUST_PRESSED: self.down = Click.PRESSED
        if self.app.user_inputs[3] and self.down == Click.NONE: self.down = Click.JUST_PRESSED
        if not self.app.user_inputs[3]:
            if (self.down == Click.PRESSED or self.down == Click.JUST_PRESSED): self.down = Click.JUST_RELEASED
            elif self.down == Click.JUST_RELEASED: self.down = Click.NONE

