# from third-party
import numpy as np

# from pybeast
from pybeast.core.agents.neuralanimat import EvoFFNAnimat
from pybeast.core.evolve.population import Population, Group
from pybeast.core.evolve.geneticalgorithm import GeneticAlgorithm, Evolver, GASelectionType, MutationOperator
from pybeast.core.sensors.sensor import NearestAngleSensor
from pybeast.core.simulation import Simulation
from pybeast.core.world.worldobject import WorldObject
from pybeast.core.utils.colours import ColourPalette, ColourType

IsDemo = True
GUIName = 'EvoMouse'
SimClassName = 'EvoMouseSimulation'

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

class EvoMouse(EvoFFNAnimat):
    """
    In an ideal world, EvoMouse would inherit from Mouse, thereby getting the same OnCollision function and
    initialisation code as Mouse, but it's more convenient to inherit from EvoFFNAnimat which gives us all
    the GA and FFN code. Multiple inheritance would be another option, but introduces a host of other unwanted
    complications.

    """

    def __init__(self):
        """Initialize a new EvoMouse."""

        super().__init__()

        self.cheesesFound = 0
        self.SetSolid(False)
        self.SetRadius(10)

        sensorRange = 400
        self.AddSensor("angle", NearestAngleSensor(Cheese, range=sensorRange))
        self.SetInteractionRange(sensorRange)
        # Initialize feed forward network
        self.AddFFNBrain(4)

    def Control(self):
        """
        Overwrite EvoFFNAnimat control method
        """
        # Make brain fire, output is in the range [-1.0, 1.0]
        # Here, we add a bias to ensure that animats control is between 0 and 1
        super().Control()

        for n, k in enumerate(self.controls.keys()):
            self.controls[k] = self.controls[k] + 0.5

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

    def GetFitness(self) -> float:
        """
        The EvoMouse's fitness is the amount of cheese collected, divided by
	    the distance travelled, so a mouse is penalised for simply charging around
	    as fast as possible and therby randomly collecting cheese - it needs to find
	    its the cheese efficiently.
        """
        #return self.cheesesFound / np.log10(self.distanceTravelled) if self.cheesesFound > 0 else 0.0
        return self.cheesesFound


class EvoMouseSimulation(Simulation):
    """Represents a simulation with mice and cheese."""

    def __init__(self):
        """Initialize a new MouseSimulation."""
        super().__init__('Mouse')

        # Simulation runs for 100 generations
        self.SetGenerations(100)
        # One assessment per generation
        self.SetAssessments(1)
        # Each assessment runs for 500 timesteps
        self.SetTimeSteps(500)

        popSize = 30
        self.theGA = GeneticAlgorithm( 0.25,0.1, selection = GASelectionType.GA_ROULETTE)

        self.theGA.SetSelection(GASelectionType.GA_ROULETTE)
        self.Add('theMice', Population(popSize, EvoMouse, self.theGA))
        self.Add('thecheese', Group(popSize, Cheese))

        self.sleepBetweenLogs = 0.0

        for k in ['Simulation', 'Run', 'Generation']: #, 'Assessment', 'Update']:
            self.whatToLog[k] = True

        self.whatToSave['Simulation'] = self.whatToSave['Run'] = self.whatToSave['Generation'] = True

    def LogEndGeneration(self):

        super().LogEndGeneration()
        self.logger.info(f'Average fitness {self.avgFitness:.5f}')

    def CreateDataStructSimulation(self):
        self.data = {}

    def CreateDataStructRun(self):
        self.averageFitness = []

    def SaveGeneration(self):

        self.avgFitness = np.mean(self.contents['theMice'].AverageFitnessScoreOfMembers())
        self.averageFitness.append(self.avgFitness)

        return

    def SaveRun(self):

        self.data[f'Run{self.Run}'] = self.averageFitness

if __name__ == '__main__':

    simulation = EvoMouseSimulation()
    simulation.RunSimulation(render=False)