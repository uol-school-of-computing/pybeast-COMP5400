# from third-party
import numpy as np
# pybeast imports
from pybeast.core.agents.animat import Animat
from pybeast.core.evolve.population import Population, Group
from pybeast.core.evolve.geneticalgorithm import GeneticAlgorithm, Evolver, GASelectionType
from pybeast.core.sensors.sensor import NearestAngleSensor
from pybeast.core.simulation import Simulation
from pybeast.core.world.worldobject import WorldObject
from pybeast.core.utils.colours import ColourPalette, ColourType

IsDemo = True
GUIName = 'Mouse'
SimClassName = 'MouseSimulation'

#================================================================================================
# Define cheese objects
#================================================================================================

class Cheese(WorldObject):
    """Represents a cheese object."""

    def __init__(self):
        """Initialize a new Cheese object."""
        super().__init__()
        self.SetRadius(5.0)
        self.SetResetRandom(True)
        self.SetColour(*ColourPalette[ColourType.COLOUR_YELLOW])

    def Eaten(self):
        """Handle the event when the cheese is eaten."""
        self.location = self.myWorld.RandomLocation()

#================================================================================================
# Define mouse agent
#================================================================================================

class Mouse(Animat):
    """
    In an ideal world, EvoMouse would inherit from Mouse, thereby getting the same OnCollision function and
    initialisation code as Mouse, but it's more convenient to inherit from EvoFFNAnimat which gives us all
    the GA and FFN code. Multiple inheritance would be another option, but introduces a host of other unwanted
    complications.

    """
    def __init__(self):
        """Initialize a new EvoMouse."""

        Animat.__init__(self)

        self.cheesesFound = 0
        range = 250
        self.AddSensor("angle", NearestAngleSensor(Cheese, range = range))
        self.SetInteractionRange(range)
        self.SetMaxSpeed(100.0)
        self.SetMinSpeed(0.0)
        self.SetRadius(10)
    def Reset(self):
        """
        Resets mouse after assessment
        """
        self.cheesesFound = 0
        super().Reset()

    def OnCollision(self, obj):
        """
        This is identical to the OnCollision method for Mouse, except here we are also recording the number of
        cheeses eaten.
        """
        if isinstance(obj, Cheese):
            self.cheesesFound += 1
            obj.Eaten()

    def Control(self):

        o = self.sensors['angle'].GetOutput()

        self.controls["left"] =  0.5 + o
        self.controls["right"] = 0.5 - o

class MouseSimulation(Simulation):
    """Represents a simulation with mice and cheese."""

    def __init__(self):
        """Initialize a new MouseSimulation."""
        super().__init__('Mouse')

        self.SetAssessments(1)
        self.SetTimeSteps(-1)

        self.theGA = GeneticAlgorithm(0.7, 0.05)
        self.theGA.SetSelection(GASelectionType.GA_RANK)
        self.theGA.SetFltParameter('GA_RANK_SPRESSURE', 2.0)

        theMice = Group(30, Mouse)
        theCheeses = Group(30, Cheese)

        self.Add('theMice', theMice)
        self.Add('thecheese', theCheeses)

        self.whatToSave['Simulation'] = self.whatToSave['Run'] = self.whatToSave['Generation'] = True

if __name__ == '__main__':

    sim = MouseSimulation()
    sim.profile = False
    sim.RunSimulation(render=False)
