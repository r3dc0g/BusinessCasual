import pyglet
import pyglet.gl as gl
import pyglet
import arcade

class MyWindow(arcade.Window):


    def on_draw(self):
        print("Draw")
        white = (0, 255, 255, 255)
        label = pyglet.text.Label("Hi",
                                  font_name="Arial",
                                  font_size=20,
                                  x=50, y=50, color=white)
        label.draw()


win = MyWindow()
pyglet.app.run()