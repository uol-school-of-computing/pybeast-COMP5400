# Third-party
import numpy as np

from pybeast.core.simulation import Simulation
from pybeast.core.world.drawable import Drawable
# Pybeast
from pybeast.core.world.worldobject import WorldObject
from pybeast.core.agents.animat import Animat
from pybeast.core.sensors.sensor import ProximitySensor
from pybeast.core.utils.vector2D import Vector2D
from pybeast.core.utils.colours import  ColourPalette, ColourType

IsDemo = True
GUIName = 'Braitenberg'
SimClassName = 'BraitenbergSimulation'

class Dot(WorldObject):
    """Dots are WorldObjects with the colour set to yellow and the radius set to 10."""
    def __init__(self, l=Vector2D()):
        """Constructor allowing to specify a location."""
        super().__init__(l, 0.0, 12.5)
        self.SetColour(*ColourPalette[ColourType.COLOUR_YELLOW])

    def __del__(self):
        """Destructor."""
        pass

class Braitenberg(Animat):
    """Braitenberg class representing a basic bot with sensors."""

    def __init__(self):
        """Initialize a Braitenberg object."""

        super().__init__(randomColour=False)

        self.AddSensor("left", ProximitySensor(Dot, np.pi/2.0, 125,  +np.pi/2.5, simple=True, outputMaximum=0.5))
        self.AddSensor("right", ProximitySensor(Dot, np.pi/2.0, 125, -np.pi/2.5, simple=True, outputMaximum=0.5))

        self.sensors['left'].SetDrawFixed(True)
        self.sensors['right'].SetDrawFixed(True)

        self.SetMinSpeed(20.0)
        self.SetMaxSpeed(90.0)
        self.SetTimeStep(0.05)
        self.SetRadius(10.0)
        self.SetMaxRotationSpeed(2*np.pi)

    def Control(self):
        # Add stuff to default Control here

        self.controls["left"] = self.sensors['right'].GetOutput()
        self.controls["right"] = self.sensors['left'].GetOutput()

    def Update(self):
        # Add stuff to default Update here
        super().Update()


class Braitenberg2a(Braitenberg):
    """Braitenberg2a class representing a Braitenberg with left sensor controlling left motor."""

    def __init__(self):

        super().__init__()
        Drawable.SetColour(self, *ColourPalette[ColourType.COLOUR_RED])

    def Control(self):
        """Override control method to set left and right controls based on left and right sensor outputs."""
        self.controls["left"] = self.sensors["left"].GetOutput()
        self.controls["right"] = self.sensors["right"].GetOutput()

class Braitenberg2b(Braitenberg):
    """Braitenberg2b class representing a Braitenberg with left sensor controlling right motor."""

    def __init__(self):

        super().__init__()
        Drawable.SetColour(self, *ColourPalette[ColourType.COLOUR_BLUE])

    def Control(self):
            """Override control method to set left and right controls based on right and left sensor outputs."""
            self.controls["left"] = self.sensors["right"].GetOutput()
            self.controls["right"] = self.sensors["left"].GetOutput()

class BraitenbergSimulation(Simulation):
    """BraitenbergSimulation class representing a simulation with Braitenberg vehicles and dots."""

    def __init__(self):
        """Initialize a BraitenbergSimulation object."""
        super().__init__('Braitenberg')

        # Simulation runs forever
        self.SetTimeSteps(-1)

    def BeginAssessment(self):

        self.theWorld.Add(Braitenberg2a())
        self.theWorld.Add(Braitenberg2b())

        # Add Dots
        positions = [(150.0, 100.0), (200.0, 100.0), (250.0, 100.0), (300.0, 100.0),
                     (350.0, 100.0), (350.0, 150.0), (350.0, 200.0),
                     (350.0, 250.0), (350, 300.0), (350.0, 350.0),
                     (300.0, 350.0), (250.0, 350.0), (200.0, 350.0), (200.0, 400.0),
                     (200.0, 450.0), (200.0, 500.0), (200.0, 550.0), (250.0, 550.0),
                     (300.0, 550.0), (350.0, 550.0), (400.0, 550.0), (450.0, 550.0),
                     (500.0, 550.0), (550.0, 550.0), (600.0, 550.0), (600.0, 500.0),
                     (600.0, 450.0), (600.0, 400.0), (600.0, 350.0), (550.0, 350.0),
                     (500.0, 350.0), (500.0, 300.0), (500.0, 250.0), (500.0, 200.0),
                     (500.0, 150.0), (500.0, 100.0), (500.0, 50.0)]


        for pos in positions:
            self.theWorld.Add(Dot(Vector2D(pos[0], pos[1])))

        super().BeginAssessment()

if __name__ == "__main__":
    simulation = BraitenbergSimulation()