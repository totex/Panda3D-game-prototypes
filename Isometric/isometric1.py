from direct.showbase.ShowBase import ShowBase
from panda3d.core import loadPrcFileData, BitMask32, Vec3
from panda3d.core import CollisionTraverser, CollisionNode
from panda3d.core import CollisionHandlerQueue, CollisionRay
# from panda3d.core import OrthographicLens

config_vars = """
win-size 1280 720
show-frame-rate-meter 1
"""

loadPrcFileData("", config_vars)

HIGHLIGHT = (0, 1, 1, 1)
WHITE = (1, 1, 1, 1)


class IsometricGame(ShowBase):
    def __init__(self):
        super().__init__()
        self.set_background_color(0, 0, 0, 1)

        # set the camera to the correct position to create an isometric view
        self.cam.setPos(0, -6, 0)  # set cam global position
        self.cam.setR(45)  # set cam global Roll rotation
        self.cam.setP(self.cam, 65)  # set cam local Pitch rotation
        self.cam.setPos(self.cam, self.cam.getPos() + Vec3(0, 0, -4))  # set cam local position

        # load the 3D models
        self.plane = self.loader.loadModel("egg-models/plane")
        self.tex1 = self.loader.loadTexture("egg-models/tex/brick-c.jpg")
        self.plane.setTexture(self.tex1)

        self.cube = self.loader.loadModel("models/box")
        self.cube.setPos(0, -1, 0)
        self.cube.reparentTo(self.render)

        # create an empty node path
        self.my_map = self.render.attachNewNode("iso-map")
        # fill the empty node path with grid tiles
        self.create_map(10, 10)

        # collision detection objects - traverser, handler, node, ray
        self.picker = CollisionTraverser()
        self.queue = CollisionHandlerQueue()
        picker_node = CollisionNode('picker-node')
        picker_node.setFromCollideMask(BitMask32.bit(1))
        picker_np = self.cam.attachNewNode(picker_node)
        self.picker_ray = CollisionRay()
        picker_node.addSolid(self.picker_ray)
        self.picker.addCollider(picker_np, self.queue)
        # self.picker.showCollisions(self.render)

        self.taskMgr.add(self.mouse_task, 'mouse-task')
        self.hit = False

        # accepting keyboard input events, and binding the move method
        self.accept("arrow_left", self.move, ["left"])
        self.accept("arrow_right", self.move, ["right"])
        self.accept("arrow_up", self.move, ["up"])
        self.accept("arrow_down", self.move, ["down"])

        # If you want to use orthographic projection:
        # on top of this file just import the following: from panda3d.core import OrthographicLens
        # Than uncomment the code below.
        # lens = OrthographicLens()
        # lens.setFilmSize(16, 9)
        # lens.setNearFar(-50, 50)
        # self.cam.node().setLens(lens)

    def move(self, direction):
        """ Moves the cube on the grid. """
        if direction == "left":
            self.cube.setPos(self.cube.getPos() + Vec3(-1, 0, 0))
        elif direction == "right":
            self.cube.setPos(self.cube.getPos() + Vec3(1, 0, 0))
        elif direction == "up":
            self.cube.setPos(self.cube.getPos() + Vec3(0, 0, 1))
        elif direction == "down":
            self.cube.setPos(self.cube.getPos() + Vec3(0, 0, -1))

    def mouse_task(self, task):
        """ Checks the mouse position and detects mouse hover. """
        if self.hit is not False:
            # print(self.hit)
            self.my_map.getChild(self.hit).setColor(WHITE)
            self.hit = False

        if self.mouseWatcherNode.hasMouse():
            m_pos = self.mouseWatcherNode.getMouse()

            # cast a ray, and traverse tha map to detect which tile was hit by the ray
            self.picker_ray.setFromLens(self.camNode, m_pos.getX(), m_pos.getY())
            self.picker.traverse(self.my_map)

            if self.queue.getNumEntries() > 0:
                # if we have hits, sort the hits so that the closest is first, and highlight that node
                self.queue.sortEntries()

                tile = self.queue.getEntry(0).getIntoNodePath().getNode(2)  # getNode(2)->tile node, at index 2
                tile_index = int(tile.getName().split("-")[1])
                self.my_map.getChild(tile_index).setColor(HIGHLIGHT)
                self.hit = tile_index

        return task.cont

    def create_map(self, width, height):
        """ Creates a 2D grid of of tiles. """
        counter = 0
        for z in range(height):
            for x in range(width):
                tile = self.my_map.attachNewNode("tile-" + str(counter))
                tile.setPos(x, 0, z)
                self.plane.instanceTo(tile)  # first we have to create an instance, after this we can set the BitMask
                tile.find("**/pPlane1").node().setIntoCollideMask(BitMask32.bit(1))
                counter += 1


game = IsometricGame()
game.run()
