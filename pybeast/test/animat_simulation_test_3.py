# Third-party
import numpy as np

from pybeast.core.simulation import Simulation
# Pybeast
from pybeast.core.world.world import WORLD_DISP_PARAM
from pybeast.core.utils.vector2D import Vector2D
from pybeast.core.agents.animat import Animat
from pybeast.core.sensors.sensor import ProximitySensor

class Braitenberg(Animat):
    """Braitenberg class representing a basic bot with sensors."""

    def __init__(self):
        """Initialize a Braitenberg object."""

        startLocoation = Vector2D(0.5*WORLD_DISP_PARAM.width, 0.5*WORLD_DISP_PARAM.height)
        super().__init__(startLocation = startLocoation, startOrientation = 0.5*np.pi)

        self.controlMax = 0.5
        self.controlMin = 0.25
        self.p = 0.3

        self.controls['left'] = self.controlMax
        self.controls['right'] = self.controlMin

        self.AddSensor("left", ProximitySensor(None, np.pi/4, 75.0, np.pi/4))
        self.AddSensor("right", ProximitySensor(None, np.pi/4, 75.0, -np.pi/4))

        for s in self.sensors.values():
            s.SetWrapping(False)

        self.SetMinSpeed(50.0)
        self.SetMaxSpeed(150.0)
        self.SetRadius(10.0)

    def Update(self):

        if np.random.rand() <= self.p:

            if self.controls['left'] == self.controlMax:
                self.controls['left'] = self.controlMin
                self.controls['right'] = self.controlMax
            else:
                self.controls['left'] = self.controlMax
                self.controls['right'] = self.controlMin

        super().Update()

class AnimatTestSimulation3(Simulation):
    """BraitenbergSimulation class representing a simulation with Braitenberg vehicles and dots."""

    def __init__(self):
        """Initialize a BraitenbergSimulation object."""
        super().__init__('AnimatTest3')

        self.assessments = 5
        self.timeSteps = 100
        self.whatToLog['Generation'] = self.whatToLog['Assessment'] = self.whatToLog['Update'] = True

    def BeginAssessment(self):
        self.theWorld.Add(Braitenberg())
        super().BeginAssessment()

if __name__ == "__main__":
    simulation = AnimatTestSimulation3()
    simulation.RunSimulation(render=True)