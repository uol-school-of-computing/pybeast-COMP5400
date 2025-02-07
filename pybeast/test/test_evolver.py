import  random
import numpy as np
from pybeast.core.agents.neuralanimat import EvoFFNAnimat
from pybeast.core.evolve.geneticalgorithm import GeneticAlgorithm, GASelectionType
from pybeast.core.evolve.population import Population
from pybeast.core.evolve.evolver import Evolver

class EvoMouse(EvoFFNAnimat, Evolver):
    """
    In an ideal world, EvoMouse would inherit from Mouse, thereby getting the same OnCollision function and
    initialisation code as Mouse, but it's more convenient to inherit from EvoFFNAnimat which gives us all
    the GA and FFN code. Multiple inheritance would be another option, but introduces a host of other unwanted
    complications.
    """

    def __init__(self):
        """Initialize a new EvoMouse."""

        EvoFFNAnimat.__init__(self)
        Evolver.__init__(self)

        # Initialize feed forward network
        self.AddFFNBrain(4)

def test_set_genome():

    outputs = random.randint(1, 4)
    inputs = random.randint(1, 4)
    hiddens = random.randint(1, 10)
    bias = np.random.choice([True, False])

    animat = EvoFFNAnimat()
    animat.AddFFNBrain(inputs, outputs, hiddens, bias=bias)
    animat.myBrain.Randomise()
    config = animat.myBrain.GetConfiguration()
    genome = animat.GetGenotype()
    animat.SetGenotype(genome)
    newConfig = animat.myBrain.GetConfiguration()

    assert config == newConfig

    print("Passed 'test_evolver.test_set_genome'!")

if __name__ == '__main__':

    test_set_genome()


