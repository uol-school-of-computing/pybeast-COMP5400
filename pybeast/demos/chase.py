# from third-party
import numpy as np
# from pybeast
from pybeast.core.simulation import Simulation
from pybeast.core.agents.neuralanimat import EvoFFNAnimat
from pybeast.core.evolve.population import Population
from pybeast.core.evolve.geneticalgorithm import GeneticAlgorithm, GASelectionType
from pybeast.core.sensors.sensor import ProximitySensor
from pybeast.core.evolve.evolver import Evolver

IsDemo = True
GUIName = 'Chase'
SimClassName = 'ChaseSimulation'

class Prey(EvoFFNAnimat, Evolver):

    def __init__(self):
        EvoFFNAnimat.__init__(self)
        Evolver.__init__(self)

        self.timesEaten = 0

        range = 300.0
        self.AddSensor('left', ProximitySensor(Predator, np.pi/4, range,  +np.pi/8, simple=True))
        self.AddSensor('right', ProximitySensor(Predator, np.pi/4, range, -np.pi/8, simple=True))
        self.SetInteractionRange(range)

        # Init brain
        self.AddFFNBrain(4)

        self.SetSolid(False)
        self.SetRadius(10)
        self.SetMinSpeed(0.0)
        self.SetMaxSpeed(100.0)

    def Control(self):
        """
        Overwrite EvoFFNAnimat control method.
        """
        super().Control()

        for k in self.controls.keys():
            self.controls[k] = 0.5 * (self.controls[k] + 1.0)

    def Eaten(self):
        """
        Gets called when prey collides with 'Predator'
        """
        self.timesEaten += 1
        # After pray has been eaten, respawn pray at random location
        self.location = self.myWorld.RandomLocation()
        self.trail.Clear()

    def GetFitness(self) -> float:
        """
        Returns prey's fitness.
        """
        if self.timesEaten == 0:
            return 1.0
        return 1.0 / self.timesEaten

    def Reset(self):
        """
        Reset prey after assessment
        """
        self.timesEaten = 0

class Predator(EvoFFNAnimat, Evolver):

    def __init__(self):
        EvoFFNAnimat.__init__(self)
        Evolver.__init__(self)

        self.preyEaten = 0
        range = 300.0
        self.AddSensor('left', ProximitySensor(Prey, np.pi/4, range,  +np.pi/8, simple=True))
        self.AddSensor('right', ProximitySensor(Prey, np.pi/4, range, -np.pi/8, simple=True))
        self.SetInteractionRange(range)

        self.AddFFNBrain(4)

        self.SetSolid(False)
        self.SetMinSpeed(0.0)
        self.SetMaxSpeed(110.0)
        self.SetRadius(20.0)

    def Control(self):
        """
        Overwrite EvoFFNAnimat control method.
        """
        super().Control()

        for k in self.controls.keys():
            self.controls[k] = 0.5 * (self.controls[k] + 1.0)

    def OnCollision(self, obj):

        if isinstance(obj, Prey):
            self.preyEaten += 1
            obj.Eaten()

        super().OnCollision(obj)

    def GetFitness(self):
        return self.preyEaten

    def Reset(self):
        """
        Reset prey after assessment
        """
        self.preyEaten = 0

class ChaseSimulation(Simulation):

    def __init__(self):
        super().__init__('Chase')

        self.SetRuns(1)
        # Simulation runs for 2000 generations
        self.SetGenerations(2000)
        # One assessment per generation
        self.SetAssessments(3)
        # Each assessment runs for 500 timesteps
        self.SetTimeSteps(500)

        popSizePrey, popSizePred = 30, 30

        gaPrey = GeneticAlgorithm(0.25, 0.1, selection = GASelectionType.GA_ROULETTE)
        gaPred = GeneticAlgorithm(0.25, 0.1, selection = GASelectionType.GA_ROULETTE)

        self.Add('prey', Population(popSizePrey, Prey, gaPrey, teamsize = 10))
        self.Add('predator', Population(popSizePred, Predator, gaPred, teamsize = 10))

        # Specify what to log
        self.whatToLog['Simulation'] = self.whatToLog['Run'] = self.whatToLog['Generation'] = self.whatToLog['Assessment'] =True

if __name__ == "__main__":

    simulation = ChaseSimulation()
    simulation.RunSimulation(render=False)