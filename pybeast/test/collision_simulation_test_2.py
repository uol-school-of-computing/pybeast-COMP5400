# Third-party
import time

import numpy as np

from pybeast.core.simulation import Simulation
# Pybeast
from pybeast.core.agents.animat import Animat
from pybeast.core.utils.vector2D import Vector2D
from pybeast.core.world.drawable import Drawable
from pybeast.core.world.world import WORLD_DISP_PARAM
from pybeast.core.world.worldobject import WorldObject
from pybeast.core.utils.colours import ColourPalette, ColourType

IsDemo = True
GUIName = 'CollisionTest2'
SimClassName = 'CollisionTestSimulation2'

class Dot(WorldObject):
    """Dots are WorldObjects with the colour set to yellow and the radius set to 10."""
    def __init__(self, l=Vector2D()):
        """Constructor allowing to specify a location."""
        super().__init__(l, 0.0, 10.0, solid=True, initRandom=True)
        self.SetColour(*ColourPalette[ColourType.COLOUR_YELLOW])

    def __del__(self):
        """Destructor."""
        pass

class Braitenberg(Animat):
    """Braitenberg class representing a basic bot with sensors."""

    def __init__(self):
        """Initialize a Braitenberg object."""

        self.centre = Vector2D(0.5*WORLD_DISP_PARAM.width, 0.5*WORLD_DISP_PARAM.height)
        super().__init__(startLocation = self.centre, startOrientation = 2*np.pi*np.random.rand(), initRandom=True)

        # Set Velocity to zero
        self.SetVelocity(Vector2D())
        self.SetMinSpeed(0.0)
        self.trail.visible = False

    def Control(self):

        # Set contorls to zero so that animats don't move
        self.controls['left'] = 0.0
        self.controls['right'] = 0.0

    def Update(self):

        self.SetLocation(self.myWorld.RandomLocation())
        #super().Update()

        return

class CollisionTestSimulation2(Simulation):
    """BraitenbergSimulation class representing a simulation with Braitenberg vehicles and dots."""

    def __init__(self):
        """Initialize a BraitenbergSimulation object."""
        super().__init__()

        # Display collisions
        self.theWorld.worldDisplayType.DISPLAY_COLLISIONS = 16

        NAnimats = 10
        R1 = 20
        NDots = 10
        R2 = 20

        for _ in range(NAnimats):
            bb = Braitenberg()
            bb.SetRadius(R1)
            self.theWorld.Add(bb)

        for _ in range(NDots):
            dot = Dot()
            dot.SetRadius(R2)
            self.theWorld.Add(dot)

    def Update(self):
        print(len(self.theWorld.collisions))
        super().Update()
        time.sleep(1.0)

if __name__ == "__main__":
    simulation = CollisionTestSimulation2()