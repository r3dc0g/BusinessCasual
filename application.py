import os
import sys
import random

parent_dir = os.path.abspath(os.path.dirname(__file__))
vendor_dir = os.path.join(parent_dir, 'vendor')

sys.path.append(vendor_dir)


import arcade

'''Constants'''
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 650
SCREEN_TITLE = "Business Casual"

'''Sprite Constants'''
CHARACTER_SCALING = .33
TILE_SCALING = .5
ITEM_SCALING = .5
PLAYER_MOVEMENT_SPEED = 5

'''Physics Constants'''
GRAVITY = 1
PLAYER_JUMP_SPEED = 20

'''Scrolling Constants'''
LEFT_MARGIN = 250
RIGHT_MARGIN = 250
BOTTOM_MARGIN = 50
TOP_MARGIN = 100

class BusinessCasual(arcade.Window):
    
    """
    Main Application Class
    """

    def __init__(self):

        '''initializes the window'''
         
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)

        '''Item, Character, and Wall lists'''
        self.item_list = None
        self.wall_list = None
        self.player_list = None

        '''Player Sprite'''
        self.player_sprite = None

        '''Physics Engine'''
        self.physics_engine = None

        '''Used to keep track of scrolling'''
        self.view_bottom = 0
        self.view_left = 0

        arcade.set_background_color(arcade.csscolor.CORNFLOWER_BLUE)

    def setup(self):
        
        self.player_list = arcade.SpriteList()
        self.item_list = arcade.SpriteList()
        self.wall_list = arcade.SpriteList()

        '''Set up Player Character'''
        image_source = os.path.join(__file__, os.getcwd() + "/Assets/Main Character Frames/000.png")
        self.player_sprite = arcade.Sprite(image_source, CHARACTER_SCALING)
        self.player_sprite.center_x = 64
        self.player_sprite.center_y = 128
        self.player_list.append(self.player_sprite)

        '''Create Ground'''
        for x in range(0, 1250, 64):
            wall = arcade.Sprite(":resources:images/tiles/grassMid.png", TILE_SCALING)
            wall.center_x = x
            wall.center_y = 32
            self.wall_list.append(wall)

        '''Put Some Crates on the ground'''
        #   Coordinates for crates
        coordinate_list = [[512, 96],
                           [256, 96],
                           [768, 96]]

        for coordinate in coordinate_list:
            wall = arcade.Sprite(":resources:images/tiles/boxCrate_double.png", TILE_SCALING)
            wall.position = coordinate
            self.wall_list.append(wall)

        '''Creates Physics Engine'''
        self.physics_engine = arcade.PhysicsEnginePlatformer(self.player_sprite, self.wall_list, GRAVITY)

    def on_draw(self):
        
        '''Renders everything'''
        
        arcade.start_render()

        self.player_list.draw()
        self.wall_list.draw()
        self.item_list.draw()

    def on_key_press(self, key, modifiers):
        """Used when the user presses down on the key"""

        if key == arcade.key.UP or key == arcade.key.W:
            if self.physics_engine.can_jump():
                self.player_sprite.change_y = PLAYER_JUMP_SPEED
        if key == arcade.key.DOWN or key == arcade.key.S:
            self.player_sprite.change_y = -PLAYER_MOVEMENT_SPEED
        if key == arcade.key.LEFT or key == arcade.key.A:
            self.player_sprite.change_x = -PLAYER_MOVEMENT_SPEED
        if key == arcade.key.RIGHT or key == arcade.key.D:
            self.player_sprite.change_x = PLAYER_MOVEMENT_SPEED
    
    def on_key_release(self, key, modifiers):
        """Used when the user releases the key"""

        if key == arcade.key.LEFT or key == arcade.key.A:
            self.player_sprite.change_x = 0
        if key == arcade.key.RIGHT or key == arcade.key.D:
            self.player_sprite.change_x = 0

    def on_update(self, delta_time):
        """Logic and Movement"""

        '''Updates the physics engine'''
        self.physics_engine.update()
 
    # === Scrolling ===

        changed = False

        '''Scroll Left'''
        left_boundary = self.view_left + LEFT_MARGIN
        if self.player_sprite.left < left_boundary:
            self.view_left -= left_boundary - self.player_sprite.left
            changed = True

        '''Scroll Right'''
        right_boundary = self.view_left + SCREEN_WIDTH - RIGHT_MARGIN
        if self.player_sprite.right > right_boundary:
            self.view_left += self.player_sprite.right - right_boundary
            changed = True

        '''Scroll Up'''
        top_boundary = self.view_bottom + SCREEN_HEIGHT - TOP_MARGIN
        if self.player_sprite.top > top_boundary:
            self.view_bottom += self.player_sprite.top - top_boundary
            changed = True

        '''Scroll Down'''
        bottom_boundary = self.view_bottom + BOTTOM_MARGIN
        if self.player_sprite.bottom < bottom_boundary:
            self.view_bottom -= bottom_boundary - self.player_sprite.bottom
            changed = True

        if changed:

            #Scrolls using integers
            self.view_bottom = int(self.view_bottom)
            self.view_left = int(self.view_left)

            '''Scroll'''
            arcade.set_viewport(self.view_left, SCREEN_WIDTH + self.view_left, self.view_bottom, SCREEN_HEIGHT + self.view_bottom)


def main():
        
    '''Main Method'''

    window = BusinessCasual()
    window.setup()
    arcade.run()

if __name__ == "__main__":
    main()
