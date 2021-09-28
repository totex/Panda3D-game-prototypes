from direct.showbase.ShowBase import ShowBase
from panda3d.core import loadPrcFileData, Vec3
from light_setup import setup_point_light
from panda3d.core import CollisionBox, CollisionTraverser, CollisionHandlerQueue, CollisionNode, BitMask32

configVars = """
win-size 1280 720
show-frame-rate-meter 1
"""

loadPrcFileData("", configVars)

key_map = {
    "left": False,
    "right": False,
}


def update_key_map(control_name, state):
    """ This function is called when the left or right keys are pressed or released. It updates the key_map dict."""
    key_map[control_name] = state


class Platformer(ShowBase):
    def __init__(self):
        super().__init__()
        self.set_background_color(0, 0, 0, 1)
        self.cam.setPos(0, -65, 15)

        # loading the Player character
        self.player = self.loader.loadModel("egg-models/player")
        self.player.find("**/Player").node().setIntoCollideMask(BitMask32.bit(2))
        self.player.reparentTo(self.render)

        # loading the floor and the platforms
        self.floor = self.loader.loadModel("egg-models/floor")
        self.floor.reparentTo(self.render)

        # setup the lights
        setup_point_light(self.render, (15, 0, 20))

        # keyboard input events
        self.accept("arrow_left", update_key_map, ["left", True])
        self.accept("arrow_left-up", update_key_map, ["left", False])
        self.accept("arrow_right", update_key_map, ["right", True])
        self.accept("arrow_right-up", update_key_map, ["right", False])
        self.accept("arrow_up", self.jump)

        # adding the update method to the Task manager
        self.taskMgr.add(self.update, "update")

        # Movement vectors
        self.position = Vec3(0, 0, 30)  # This is also the initial position of the Player
        self.velocity = Vec3(0, 0, 0)
        self.acceleration = Vec3(0, 0, 0)

        # Constants
        self.SPEED = 4
        self.GRAVITY = -0.05
        self.JUMP_FORCE = 1.2
        self.FRICTION = -0.12  # THIS HAS TO BE A NEGATIVE NUMBER

        # setting up the collision detection
        self.cTrav = CollisionTraverser()
        self.queue = CollisionHandlerQueue()
        collider_node = CollisionNode("box-coll")  # collision node for the Player
        coll_box = CollisionBox((-1, -1, 0), (1, 1, 4))  # collision geometry for the Player
        collider_node.setFromCollideMask(BitMask32.bit(1))
        collider_node.addSolid(coll_box)
        collider = self.player.attachNewNode(collider_node)
        self.cTrav.addCollider(collider, self.queue)
        # collider.show() # shows the debug box

        # Jump variables
        self.is_jumping = False
        self.is_on_floor = True
        self.jump_count = 0

    def jump(self):
        """ When the up arrow is pressed this method runs. """
        if self.is_on_floor:
            self.is_jumping = True
            self.is_on_floor = False
            self.velocity.z = self.JUMP_FORCE
            self.jump_count += 1
            if self.jump_count == 2:
                self.is_jumping = False
                self.is_on_floor = True
                self.jump_count = 0

    def update(self, task):
        """ The update method is called every frame by the Task manager. """
        dt = globalClock.getDt()

        self.acceleration = Vec3(0, 0, self.GRAVITY)

        if key_map["right"]:  # if right is True
            self.acceleration.x = self.SPEED * dt
        if key_map["left"]:  # if left is True
            self.acceleration.x = -self.SPEED * dt

        # calculating the position vector based on the velocity and the acceleration vectors
        self.acceleration.x += self.velocity.x * self.FRICTION  # Only add Friction to horizontal movement
        self.velocity += self.acceleration
        self.position += self.velocity + (self.acceleration * 0.5)

        for entry in self.queue.getEntries():
            # inp = into node path
            inp = entry.getIntoNodePath().getPos(self.render)  # returns LPoint3f()

            if self.velocity.z < 0:  # prevent snapping to the top of the platforms
                if not self.is_jumping:
                    self.position.z = inp.z
                    self.velocity.z = 0  # prevent fast falling from platforms
                    self.is_on_floor = True
                else:
                    self.is_jumping = False

        # setting the player's position
        self.player.setPos(self.position)

        # follow the character with the camera
        self.cam.setX(self.position.x)

        return task.cont


game = Platformer()
game.run()
