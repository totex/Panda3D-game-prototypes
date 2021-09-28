from direct.showbase.ShowBase import ShowBase
from panda3d.core import loadPrcFileData

configVars = """
win-size 1280 720
show-frame-rate-meter 1
"""

loadPrcFileData("", configVars)


class MyGame(ShowBase):
    def __init__(self):
        super().__init__()
        self.set_background_color(0, 0, 0, 1)


game = MyGame()
game.run()
