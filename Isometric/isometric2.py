from panda3d.core import loadPrcFileData, Vec3
from direct.showbase.ShowBase import ShowBase
from panda3d.core import CollisionTraverser, CollisionNode, BitMask32
from panda3d.core import CollisionHandlerQueue, CollisionRay

config_vars = """
win-size 1280 720
show-frame-rate-meter 1
"""

loadPrcFileData("", config_vars)


WHITE = (1, 1, 1, 1)
HIGHLIGHT = (1, 0, 0, 1)


class IsometricGame2(ShowBase):
    def __init__(self):
        super().__init__()
        self.set_background_color(0, 0, 0, 1)
        self.wireframeOn()

        # set the camera to the correct position to create an isometric view
        self.cam.setPos(0, -12, 0)  # set cam global position
        self.cam.setR(45)  # set cam global Roll rotation
        self.cam.setP(self.cam, 65)  # set cam local Pitch rotation
        self.cam.setPos(self.cam, self.cam.getPos() + Vec3(0, 0, -8))  # set cam local position

        # loading the 3D models
        self.corner = self.loader.loadModel("egg-models/corner")
        self.right = self.loader.loadModel("egg-models/right")
        self.left = self.loader.loadModel("egg-models/left")
        self.top = self.loader.loadModel("egg-models/top")

        # creating the map
        self.my_map = self.render.attachNewNode("iso-map")
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

        self.hit = False
        self.taskMgr.add(self.mouse_task, 'mouse-task')

    def mouse_task(self, task):
        """ Checks the mouse position and detects mouse hover. """

        # if self.hit is not false set the tile color back to its default
        if self.hit is not False:
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
                print(tile.getName())
                tile_index = int(tile.getName().split("-")[1])
                self.my_map.getChild(tile_index).setColor(HIGHLIGHT)
                self.hit = tile_index

        return task.cont

    def create_map(self, width, height):
        """ Creates the map using instancing, also sets the into collision masks. """
        counter = 0
        for z in range(height):
            for x in range(width):
                tile = self.my_map.attachNewNode("tile-" + str(counter))
                if x == 0 and z == 0:
                    tile.setPos(x, 0, z)
                    self.corner.instanceTo(tile)
                    tile.find("**/corner").node().setIntoCollideMask(BitMask32.bit(1))
                elif x == 0 and z > 0:
                    tile.setPos(x, 0, z * 2)
                    self.left.instanceTo(tile)
                    tile.find("**/left").node().setIntoCollideMask(BitMask32.bit(1))
                elif x > 0 and z == 0:
                    tile.setPos(x * 2, 0, z)
                    self.right.instanceTo(tile)
                    tile.find("**/right").node().setIntoCollideMask(BitMask32.bit(1))
                else:
                    tile.setPos(x * 2, 0, z * 2)
                    self.top.instanceTo(tile)
                    tile.find("**/top").node().setIntoCollideMask(BitMask32.bit(1))
                counter += 1


game = IsometricGame2()
game.run()
