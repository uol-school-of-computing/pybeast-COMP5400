# Third-party
import numpy as np

from pybeast.core.simulation import Simulation
# Pybeast
from pybeast.core.agents.animat import Animat
from pybeast.core.utils.vector2D import Vector2D
from pybeast.core.world.world import WORLD_DISP_PARAM

IsDemo = True
GUIName = 'CollisionTest1'
SimClassName = 'CollisionTestSimulation1'

class Braitenberg(Animat):
    """Braitenberg class representing a basic bot with sensors."""

    def __init__(self):
        """Initialize a Braitenberg object."""

        self.centre = Vector2D(0.5*WORLD_DISP_PARAM.width, 0.5*WORLD_DISP_PARAM.height)
        super().__init__(startLocation = self.centre, startOrientation = 2*np.pi*np.random.rand())
        self.SetMinSpeed(0.0)
        self.trail.visible = False

    def Control(self):

        # Set contorls to zero so that animats don't move
        self.controls['left'] = 0.0
        self.controls['right'] = 0.0

    def Update(self):

        D = 0.75 * self.myWorld.mySimulation.D * np.random.rand()
        o = 2*np.pi * np.random.rand()
        self.SetLocation(self.centre + Vector2D(l=D, a=o))

        super().Update()

        return

class CollisionTestSimulation1(Simulation):
    """BraitenbergSimulation class representing a simulation with Braitenberg vehicles and dots."""

    def __init__(self):
        """Initialize a BraitenbergSimulation object."""
        super().__init__('CollisionTest1')

        # Display collisions
        self.theWorld.worldDisplayType.DISPLAY_COLLISIONS = 16

        self.R1, self.R2 = 10, 10
        self.D = self.R1 + self.R2

        bb1 = Braitenberg()
        bb1.SetRadius(self.R1)
        bb2 = Braitenberg()
        bb2.SetRadius(self.R2)

        self.theWorld.Add(bb1)
        self.theWorld.Add(bb2)

    def Update(self):
        super().Update()

if __name__ == "__main__":
    simulation = CollisionTestSimulation1()