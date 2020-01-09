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
CURRENT_DIRECTORY = os.getcwd()

'''Sprite Constants'''
CHARACTER_SCALING = .5
TILE_SCALING = .5
ITEM_SCALING = .5
PLAYER_MOVEMENT_SPEED = 5
PLAYER_START_X = 64
PLAYER_START_Y = 225
SPRITE_PIXEL_SIZE = 128
GRID_PIXEL_SIZE = (SPRITE_PIXEL_SIZE * TILE_SCALING)

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
        self.background_list = None
        self.foreground_list = None
        self.traps_list = None
        self.player_list = None

        '''Player Sprite'''
        self.player_sprite = None

        '''Physics Engine32'''
        self.physics_engine = None

        '''Used to keep track of scrolling'''
        self.view_bottom = 0
        self.view_left = 0

        arcade.set_background_color(arcade.csscolor.CORNFLOWER_BLUE)

        '''Level'''
        self.level = 1
        
        '''End of the Map'''
        self.end_of_map = 0



    def setup(self, level):
        
        self.player_list = arcade.SpriteList()
        self.background_list = arcade.SpriteList()
        self.foreground_list = arcade.SpriteList()
        self.item_list = arcade.SpriteList()
        self.traps_list = arcade.SpriteList()
        self.wall_list = arcade.SpriteList()

        '''Set up Player Character'''
        image_source = f"{CURRENT_DIRECTORY}/Assets/Main Character Frames/000.png" 
        self.player_sprite = arcade.Sprite(image_source, CHARACTER_SCALING)
        self.player_sprite.center_x = PLAYER_START_X
        self.player_sprite.center_y = PLAYER_START_Y
        self.player_list.append(self.player_sprite)

        # === Load the Map ===
        
        '''Gets the map for the level'''
        map_name = f"{CURRENT_DIRECTORY}/Assets/level_1_map.tmx"

        '''Map Layer Names'''
        platforms_layer_name = "platforms"

        foreground_layer_name = "foreground"

        background_layer_name = "background"

        items_layer_name = "items"
        
        traps_layer_name = "traps"
        
        '''Loads Map'''
        my_map = arcade.tilemap.read_tmx(map_name)

        self.end_of_map = my_map.map_size.width * GRID_PIXEL_SIZE
        
        '''Foreground'''
        self.foreground_list = arcade.tilemap.process_layer(my_map, foreground_layer_name, TILE_SCALING)

        '''Background'''
        self.background_list = arcade.tilemap.process_layer(my_map, background_layer_name, TILE_SCALING)

        '''Platforms'''
        self.wall_list = arcade.tilemap.process_layer(my_map, platforms_layer_name, TILE_SCALING)

        '''Items'''
        self.items_list = arcade.tilemap.process_layer(my_map, items_layer_name, TILE_SCALING)

        '''Traps'''
        self.traps_list = arcade.tilemap.process_layer(my_map, traps_layer_name, TILE_SCALING)
        


        '''Creates Physics Engine'''
        self.physics_engine = arcade.PhysicsEnginePlatformer(self.player_sprite, self.wall_list, GRAVITY)




    def on_draw(self):
        
        '''Renders everything'''
        
        arcade.start_render()

        self.player_list.draw() 
        self.wall_list.draw()
        self.wall_list.draw()
        self.items_list.draw()
        self.traps_list.draw()
        self.foreground_list.draw()
        self.background_list.draw()

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

        changed_camera = False

        '''Updates the physics engine'''
        self.physics_engine.update()

        '''Player fall off the map?'''
        if self.player_sprite.center_y < -100:
            self.player_sprite.center_x = PLAYER_START_X
            self.player_sprite.center_y = PLAYER_START_Y

            '''Set the camera to the start'''
            self.view_left = 0
            self.view_bottom = 0
            changed_camera = True

        if self.player_sprite.center_x >= self.end_of_map:

            # Advance to the next level
            self.level += 1

            # Load the next level
            self.setup(self.level)

            # Set the camera to the start
            self.view_left = 0
            self.view_bottom = 0
            changed_camera = True
 
    # === Scrolling ===

        '''Scroll Left'''
        left_boundary = self.view_left + LEFT_MARGIN
        if self.player_sprite.left < left_boundary:
            self.view_left -= left_boundary - self.player_sprite.left
            changed_camera = True

        '''Scroll Right'''
        right_boundary = self.view_left + SCREEN_WIDTH - RIGHT_MARGIN
        if self.player_sprite.right > right_boundary:
            self.view_left += self.player_sprite.right - right_boundary
            changed_camera = True

        '''Scroll Up'''
        top_boundary = self.view_bottom + SCREEN_HEIGHT - TOP_MARGIN
        if self.player_sprite.top > top_boundary:
            self.view_bottom += self.player_sprite.top - top_boundary
            changed_camera = True

        '''Scroll Down'''
        bottom_boundary = self.view_bottom + BOTTOM_MARGIN
        if self.player_sprite.bottom < bottom_boundary:
            self.view_bottom -= bottom_boundary - self.player_sprite.bottom
            changed_camera = True

        if changed_camera:

            #Scrolls using integers
            self.view_bottom = int(self.view_bottom)
            self.view_left = int(self.view_left)

            '''Scroll'''
            arcade.set_viewport(self.view_left, SCREEN_WIDTH + self.view_left, self.view_bottom, SCREEN_HEIGHT + self.view_bottom)




def main():
        
    '''Main Method'''

    window = BusinessCasual()
    window.setup(window.level)
    arcade.run()

if __name__ == "__main__":
    main()
