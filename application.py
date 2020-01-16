'''Just some tips for the user'''
print("For optimal preformance, run on Linux! :)")

'''imports needed modules for file manipulation and random'''
import os
import sys
import random

'''Imports the logger'''
import logging

logging.basicConfig(filename='BusinessCasual.log', filemode='w', level=logging.INFO)

'''Sets up the directory with all the libraries in it for use'''
parent_dir = os.path.abspath(os.path.dirname(__file__))
vendor_dir = os.path.join(parent_dir, 'vendor')

sys.path.append(vendor_dir)

logging.info('Set the lib directory to vendor')

'''imports the very much needed arcade module'''
import arcade

'''Makes sure the pyglet library doesn't cause problems getting files'''
import pyglet
pyglet.options['search_local_libs'] = True

logging.info('imported all libraries')

'''Set the current directory to the program directory'''
file_path = os.path.dirname(os.path.abspath(__file__))
os.chdir(file_path)

logging.info('Set the working directory to program directory')

'''Constants'''
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 650
SCREEN_TITLE = "Business Casual"
CURRENT_DIRECTORY = os.getcwd()

'''Sprite Constants'''
CHARACTER_SCALING = .5
TILE_SCALING = .5
ITEM_SCALING = .5
PLAYER_START_X = 1000
PLAYER_START_Y = 1500
SPRITE_PIXEL_SIZE = 128
GRID_PIXEL_SIZE = (SPRITE_PIXEL_SIZE * TILE_SCALING)
RIGHT_FACING = 1
LEFT_FACING = 0

'''Physics Constants'''
GRAVITY = 1
PLAYER_JUMP_SPEED = 20

'''Scrolling Constants'''
LEFT_MARGIN = 250
RIGHT_MARGIN = 250
BOTTOM_MARGIN = 50
TOP_MARGIN = 100

# === Function for loading textures ===

def load_texture_pair(filename):
    """
    Load a texture pair, with the second being a mirror image.
    """
    return [
        arcade.load_texture(filename, scale=CHARACTER_SCALING),
        arcade.load_texture(filename, scale=CHARACTER_SCALING, mirrored=True)
    ]

# ===== Main Character Sprite Class =====

class PlayerCharacter(arcade.Sprite):
    """
    Main Character
    """

    def __init__(self):

        logging.info('==== Initialized Main Character ====')

        '''Sets up parent class'''
        super().__init__()
       
        '''Set the Character facing right'''
        self.character_face_direction = RIGHT_FACING
        
        self.movement_speed = 10

        '''Used for fliping the texture'''
        self.cur_texture = 0
        self.cur_fight_texture = 0

        '''State tracking'''
        self.jumping = False
        self.climbing = False
        self.is_on_ladder = False
        self.is_fighting = False
    
        '''Hitbox'''
        self.points = [[-22, -86], [22, -86], [22, 86], [-22, 86]]

        # === Load Textures ===

        main_path = f"{CURRENT_DIRECTORY}/Assets/Character Models/Sir Something"
        
        '''Standing no movement'''
        self.idle_texture_pair = load_texture_pair(f"{main_path}/Sir Something Model.png")
    
        logging.info('Loaded idle textures')

        '''Jumping'''
        self.jump_texture_pair = load_texture_pair(f"{main_path}/Sir Something Jump Model.png")
        
        logging.info('Loaded jumping textures')

        '''Falling'''
        self.fall_texture_pair = load_texture_pair(f"{main_path}/Sir Something Jump Model.png")
        
        logging.info('loaded falling textures')

        '''Loading Walking Animation'''
        self.walk_textures = []
        for i in range(6):
            texture = load_texture_pair(f"{main_path}/Main Character Frames/00{i}.png")
            self.walk_textures.append(texture)
            logging.info('Loaded walking texture')
        

        '''Loading attack Animation''' 
        self.attack_textures = []
        for i in range(2):
            texture = load_texture_pair(f"{main_path}/Sir Something Attack {i}.png")
            self.attack_textures.append(texture)
            logging.info('loaded attack texture')
        
        '''Default Texture'''
        self.texture = self.idle_texture_pair[self.character_face_direction]
        logging.info('Loaded Player Default Texture')


    def update_animation(self, delta_time: float = 1/60):

        '''Figure out if we need to flip face left or right'''
        if self.change_x < 0 and self.character_face_direction == RIGHT_FACING:
            self.character_face_direction = LEFT_FACING
        elif self.change_x > 0 and self.character_face_direction == LEFT_FACING:
            self.character_face_direction = RIGHT_FACING

        '''Climbing animation'''
        if self.is_on_ladder:
            self.climbing = True
        if not self.is_on_ladder and self.climbing:
            self.climbing = False

        '''Jumping animation'''
        if self.jumping and not self.is_on_ladder:
            if self.change_y >= 0:
                self.texture = self.jump_texture_pair[self.character_face_direction]
            else:
                self.texture = self.fall_texture_pair[self.character_face_direction]
            return

        '''Idle animation'''
        if self.change_x == 0 and not self.is_fighting:
            self.texture = self.idle_texture_pair[self.character_face_direction]
            return

        '''Walking animation'''
        self.cur_texture += 1
        if self.cur_texture > 5:
            self.cur_texture = 0
        self.texture = self.walk_textures[self.cur_texture][self.character_face_direction]
        
        '''Fighting Texture'''
        self.cur_fight_texture += 1
        if self.cur_fight_texture > 1:
            self.cur_fight_texture = 0
            
        if self.is_fighting:
            self.texture = self.attack_textures[self.cur_fight_texture][self.character_face_direction]

# ===== Game Class =====

class BusinessCasual(arcade.Window):
    
    """
    Main Application Class
    """

    def __init__(self):

        # === INITIALIZATION ===

        '''initializes the window'''
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
        
        logging.info('==== Initialized Game Window ====')

        """
        '''Set the current directory to the program directory again, just to make sure'''
        os.chdir(file_path)
        """

        '''Which key was pressed'''
        self.up_pressed = False
        self.down_pressed = False
        self.left_pressed = False
        self.right_pressed = False
        self.jump_needs_reset = False
        self.attack_pressed = False

        '''Item, Character, and Wall lists'''
        self.money_list = None
        self.potion_list = None
        self.coffee_list = None
        self.wall_list = None
        self.background_list = None
        self.foreground_list = None
        self.traps_list = None
        self.player_list = None
        self.ladder_list = None

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

        '''Score'''
        self.score = 0

    def setup(self, level):
        
        logging.info('==== Entering Game Window Setup ====')

        # === Setup ===
        
        self.player_list = arcade.SpriteList()
        self.background_list = arcade.SpriteList()
        self.foreground_list = arcade.SpriteList()
        self.money_list = arcade.SpriteList()
        self.coffee_list = arcade.SpriteList()
        self.potion_list = arcade.SpriteList()
        self.traps_list = arcade.SpriteList()
        self.wall_list = arcade.SpriteList()
        self.ladder_list = arcade.SpriteList()
        
        logging.info('Setup all sprite lists')

        '''Set up Player Character'''
        self.player_sprite = PlayerCharacter()
        self.player_sprite.center_x = PLAYER_START_X
        self.player_sprite.center_y = PLAYER_START_Y
        self.player_list.append(self.player_sprite)
        
        logging.info('Loaded Player Character')

        logging.info('==== Starting to load map ===')

        # === Load the Map ===
        
        '''Map Layer Names'''
        platforms_layer_name = "platforms"

        foreground_layer_name = "foreground"

        background_layer_name = "background"

        money_layer_name = "money"
        
        potion_layer_name = "potions"

        coffee_layer_name = "coffee"

        traps_layer_name = "traps"

        ladder_layer_name = "ladders"

        logging.info('All layer names have been set')

        '''Gets the map for the level'''
        map_name = f"{CURRENT_DIRECTORY}/Assets/level_{level}_map.tmx"
        
        logging.info(f"Loaded Level {level}")

        """
        LOADING OF LAYERS
        """

        '''Loads Map'''
        my_map = arcade.tilemap.read_tmx(map_name)

        logging.info('Read .tmx file')
        
        '''Determines the edge of the map'''
        self.end_of_map = my_map.map_size.width * GRID_PIXEL_SIZE
        
        logging.info('Determined end of map')

        '''Foreground'''
        self.foreground_list = arcade.tilemap.process_layer(my_map, foreground_layer_name, TILE_SCALING)

        '''Background'''
        self.background_list = arcade.tilemap.process_layer(my_map, background_layer_name, TILE_SCALING)

        '''Platforms'''
        self.wall_list = arcade.tilemap.process_layer(my_map, platforms_layer_name, TILE_SCALING)

        '''money'''
        self.money_list = arcade.tilemap.process_layer(my_map, money_layer_name, TILE_SCALING)
        
        '''coffee'''
        self.coffee_list = arcade.tilemap.process_layer(my_map, coffee_layer_name, TILE_SCALING)
        
        '''Potions'''
        self.potion_list = arcade.tilemap.process_layer(my_map, potion_layer_name, TILE_SCALING)

        '''Traps'''
        self.traps_list = arcade.tilemap.process_layer(my_map, traps_layer_name, TILE_SCALING)
        
        '''Ladders'''
        self.ladder_list = arcade.tilemap.process_layer(my_map, ladder_layer_name, TILE_SCALING)

        logging.info('Created Sprite Lists for each map layer of tiles')

        '''Creates Physics Engine'''
        self.physics_engine = arcade.PhysicsEnginePlatformer(self.player_sprite, self.wall_list, gravity_constant=GRAVITY, ladders=self.ladder_list)
        
        logging.info('Setup physics engine')



    def on_draw(self):
        
        '''Renders everything'''
        
        logging.info('Drawing...')

        arcade.start_render()
        
        self.background_list.draw()
        self.wall_list.draw()
        self.ladder_list.draw()
        self.coffee_list.draw()
        self.money_list.draw()
        self.potion_list.draw()
        self.player_list.draw()
        self.foreground_list.draw()

        '''Draws the score'''
        score_text = f"Score: {self.score}"
        arcade.draw_text(score_text, 10 + self.view_left, 10 + self.view_bottom,
                         arcade.csscolor.BLACK, 18)

    def process_keychange(self):

        """
        Process when a key is changed from left/right or up/down
        """

        '''Up/Down'''
        if self.up_pressed and not self.down_pressed:
            if self.physics_engine.is_on_ladder():
                self.player_sprite.change_y = self.player_sprite.movement_speed
            elif self.physics_engine.can_jump():
                self.player_sprite.change_y = PLAYER_JUMP_SPEED
                self.jump_needs_reset = True
                self.player_sprite.jumping = True
        elif self.down_pressed and not self.up_pressed:
            if self.physics_engine.is_on_ladder():
                self.player_sprite.change_y = -1 * self.player_sprite.movement_speed
        
        '''on ladder movement'''
        if self.physics_engine.is_on_ladder():
            if not self.up_pressed and not self.down_pressed:
                self.player_sprite.change_y = 0
            elif self.up_pressed and self.down_pressed:
                self.player_sprite.change_y = 0
        
        '''Right/Left'''
        if self.right_pressed and not self.left_pressed:
            self.player_sprite.change_x = self.player_sprite.movement_speed
        elif self.left_pressed and not self.right_pressed:
            self.player_sprite.change_x = -1 * self.player_sprite.movement_speed
        else:
            self.player_sprite.change_x = 0

        if self.attack_pressed:
            self.player_sprite.is_fighting = True
        else:
            self.player_sprite.is_fighting = False

    def on_key_press(self, key, modifiers):
        """Used when the user presses down on the key"""

        if key == arcade.key.UP or key == arcade.key.W:
            self.up_pressed = True
        elif key == arcade.key.DOWN or key == arcade.key.S:
            self.down_pressed = True
        elif key == arcade.key.LEFT or key == arcade.key.A:
            self.left_pressed = True 
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.right_pressed = True
        elif key == arcade.key.X:
            self.attack_pressed = True

        self.process_keychange()
    
    def on_key_release(self, key, modifiers):
        """Used when the user releases the key"""
        
        if key == arcade.key.UP or key == arcade.key.W:
            self.up_pressed = False
            self.jump_needs_reset = False
            self.player_sprite.jumping = False
        elif key == arcade.key.DOWN or key == arcade.key.S:
            self.down_pressed = False
        elif key == arcade.key.LEFT or key == arcade.key.A:
            self.left_pressed = False
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.right_pressed = False
        elif key == arcade.key.X:
            self.attack_pressed = False

        self.process_keychange()

    def update(self, delta_time):
        """Logic and Movement"""

        changed_camera = False

        '''Updates the physics engine'''
        self.physics_engine.update()

        '''Update Animations'''

        if self.physics_engine.can_jump():
            self.player_sprite.can_jump = False
        else:
            self.player_sprite.can_jump = True

        if self.physics_engine.is_on_ladder() and not self.physics_engine.can_jump():
            self.player_sprite.is_on_ladder = True
            self.process_keychange()
        else:
            self.player_sprite.is_on_ladder = False
            self.process_keychange()

        self.player_list.update_animation(delta_time)

        '''Player fall off the map?'''
        if self.player_sprite.center_y < -100:
            self.player_sprite.center_x = PLAYER_START_X
            self.player_sprite.center_y = PLAYER_START_Y

            '''Set the camera to the start'''
            self.view_left = 0
            self.view_bottom = 0
            changed_camera = True
        
        '''Test to see if the player reached the end of the map'''
        if self.player_sprite.center_x >= self.end_of_map:

            '''Advance to the next level'''
            self.level += 1

            '''Load the next level'''
            self.setup(self.level)

            '''Set the camera to the start'''
            self.view_left = 0
            self.view_bottom = 0
            changed_camera = True

        '''Money Aquiring'''
        
        money_hit_list = arcade.check_for_collision_with_list(self.player_sprite,
                                                             self.money_list)

        '''Loop through each coin we hit (if any) and remove it'''
        for chaching in money_hit_list:

            '''Figure out how many points this coin is worth'''
            if 'Points' not in chaching.properties:
                print("Warning, collected money without a Points property.")
            else:
                points = int(chaching.properties['Points'])
                self.score += points

            '''Remove the money'''
            chaching.remove_from_sprite_lists()

            logging.info('Player picked up money')

        '''Getting your cup of joe'''

        coffee_hit_list = arcade.check_for_collision_with_list(self.player_sprite, self.coffee_list)

        '''Loop through each coffee cup and remove it'''
        for slurp in coffee_hit_list:
            self.player_sprite.movement_speed += 1
            slurp.remove_from_sprite_lists()
            logging.info('Player picked up Coffee')
 
        # === Scrolling ===

        '''Scroll Left'''
        left_boundary = self.view_left + LEFT_MARGIN
        if self.player_sprite.left < left_boundary:
            self.view_left -= left_boundary - self.player_sprite.left
            changed_camera = True
            logging.info('Scrolled Left')

        '''Scroll Right'''
        right_boundary = self.view_left + SCREEN_WIDTH - RIGHT_MARGIN
        if self.player_sprite.right > right_boundary:
            self.view_left += self.player_sprite.right - right_boundary
            changed_camera = True
            logging.info('Scrolled Right')

        '''Scroll Up'''
        top_boundary = self.view_bottom + SCREEN_HEIGHT - TOP_MARGIN
        if self.player_sprite.top > top_boundary:
            self.view_bottom += self.player_sprite.top - top_boundary
            changed_camera = True
            logging.info('Scrolled Up')

        '''Scroll Down'''
        bottom_boundary = self.view_bottom + BOTTOM_MARGIN
        if self.player_sprite.bottom < bottom_boundary:
            self.view_bottom -= bottom_boundary - self.player_sprite.bottom
            changed_camera = True
            logging.info('Scolled Down')

        if changed_camera:

            #Scrolls using integers
            self.view_bottom = int(self.view_bottom)
            self.view_left = int(self.view_left)

            '''Scroll'''
            arcade.set_viewport(self.view_left, SCREEN_WIDTH + self.view_left, self.view_bottom, SCREEN_HEIGHT + self.view_bottom)

# ===== Main =====

def main():
        
    '''Main Method'''

    window = BusinessCasual()
    window.setup(window.level)
    arcade.run()

    logging.info('THE GAME HAS BEGUN')

if __name__ == "__main__":
    main()
