# Third-party
import numpy as np

from pybeast.core.simulation import Simulation
# Pybeast
from pybeast.core.agents.animat import Animat
from pybeast.core.utils.vector2D import Vector2D
from pybeast.core.world.world import WORLD_DISP_PARAM

class Braitenberg(Animat):
    """Braitenberg class representing a basic bot with sensors."""

    def Control(self):
        pass

    def __init__(self):
        """Initialize a Braitenberg object."""

        self.R = 100.0
        self.Omega = 2*np.pi / 100
        self.centre = Vector2D(0.5*WORLD_DISP_PARAM.width, 0.5*WORLD_DISP_PARAM.height)

        startLocoation = self.centre + Vector2D(self.R, 0.0)

        super().__init__(startLocation = startLocoation, startOrientation = 0.5*np.pi)

        self.SetMinSpeed(0.0)
        self.SetMaxSpeed(95.0)
        self.SetRadius(10.0)

    def Update(self):

        t = self.GetWorld().mySimulation.timeStep
        phi = self.Omega * t

        x = self.R * np.cos(phi)
        y = self.R * np.sin(phi)

        self.trail.Append(self.GetLocation())
        self.trail.Update()

        self.SetOrientation((phi + np.pi/2) % (2*np.pi))
        self.SetLocation(self.centre + Vector2D(x, y))

        return

class AnimatTestSimulation1(Simulation):
    """BraitenbergSimulation class representing a simulation with Braitenberg vehicles and dots."""

    def __init__(self):
        """Initialize a BraitenbergSimulation object."""
        super().__init__('AnimatTest1')

        self.whatToLog['Generation'] = self.whatToLog['Assessment'] = self.whatToLog['Update'] = True

        self.assessments = 5
        self.timeSteps = 100

    def BeginAssessment(self):

        # Add vehicle to the world
        self.theWorld.Add(Braitenberg())
        super().BeginAssessment()

if __name__ == "__main__":

    simulation = AnimatTestSimulation1()
    simulation.RunSimulation(render=True)


