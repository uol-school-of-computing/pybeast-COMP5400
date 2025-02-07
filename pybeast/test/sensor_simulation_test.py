# Third-party
import time

import numpy as np

# Pybeast
from pybeast.core.simulation import Simulation
from pybeast.core.world.world import WORLD_DISP_PARAM
from pybeast.core.world.worldobject import WorldObject
from pybeast.core.agents.animat import Animat
from pybeast.core.sensors.sensor import ProximitySensor
from pybeast.core.utils.vector2D import Vector2D
from pybeast.core.utils.colours import  ColourPalette, ColourType

IsDemo = True
GUIName = 'TestSensor'
SimClassName = 'TestSensorSimulation'

WorldCentre = Vector2D(0.5*WORLD_DISP_PARAM.width, 0.5*WORLD_DISP_PARAM.height)
NDots = 8

class Dot(WorldObject):
    """Dots are WorldObjects with the colour set to yellow and the radius set to 10."""
    numDot = 0

    def __init__(self, location):
        """Constructor allowing to specify a location."""
        super().__init__(startLocation=location, startOrientation=0.0)

        self.SetColour(*ColourPalette[ColourType.COLOUR_YELLOW])
        self.SetRadius(10.0)

        Dot.numDot += 1
        self.id = Dot.numDot

    def __del__(self):
        """Destructor."""
        pass

class Braitenberg(Animat):
    """Braitenberg class representing a basic bot with sensors."""

    def __init__(self):
        """Initialize a Braitenberg object."""

        super().__init__(startLocation = WorldCentre, startOrientation = 0.0)

        self.AddSensor("top", ProximitySensor(Dot, np.pi/4, 150,  0))

        self.sensors['top'].SetDrawFixed(True)
        self.SetMinSpeed(0.0)
        self.SetMaxSpeed(95.0)
        self.SetRadius(10.0)

    def Update(self):
        """
        Overwrite update function to test sensor functions
        """
        for dot in self.myWorld.mySimulation.dots:
            self.sensors['top'].Interact(dot)

        # DetectedDot
        detectedDot = self.sensors['top'].EvalFunc.bestCandidate

        if detectedDot is not None:
            if detectedDot.GetColour() != ColourPalette[ColourType.COLOUR_RED]:
                detectedDot.SetColour(*ColourPalette[ColourType.COLOUR_RED])
                detectedDot.Init()
                detectedDot.Display()

        self.OffsetOrientation(2*np.pi / NDots)
        self.sensors['top'].Update()


class TestSensorSimulation(Simulation):
    """BraitenbergSimulation class representing a simulation with Braitenberg vehicles and dots."""

    def __init__(self):
        """Initialize a BraitenbergSimulation object."""
        super().__init__('TestSensor')

        self.SetRuns(1)
        self.SetGenerations(1)
        self.SetAssessments(1)
        self.SetTimeSteps(-1)
        self.whatToLog['Generation'] = self.whatToLog['Assessment'] = True

    def Update(self):

        if self.timeStep == 8:
            self.addMoreDots()

        super().Update()

        time.sleep(1)

        if self.timeStep == 16:
            return True

        return False

    def BeginAssessment(self):

        self.theWorld.Add(Braitenberg())

        # Position N dots in a circle around vehicle
        self.phi = np.linspace(0, 2*np.pi, NDots, endpoint=False)

        R = 100
        x_dot_arr = R*np.cos(self.phi)
        y_dot_arr = R*np.sin(self.phi)

        self.dots = []

        for x, y in zip(x_dot_arr, y_dot_arr):

            dot = Dot(WorldCentre + Vector2D(x, y))
            self.theWorld.Add(dot)
            self.dots.append(dot)
            
        super().BeginAssessment()

    def addMoreDots(self):

        R = 75

        x_dot_arr = R*np.cos(self.phi)
        y_dot_arr = R*np.sin(self.phi)

        for x, y in zip(x_dot_arr, y_dot_arr):

            dot = Dot(WorldCentre + Vector2D(x, y))
            dot.Init()
            self.theWorld.Add(dot)
            self.dots.append(dot)

if __name__ == "__main__":

    simulation = TestSensorSimulation()
    simulation.RunSimulation(render=True)