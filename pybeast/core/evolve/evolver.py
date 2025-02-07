from abc import ABC, abstractmethod
from typing import TypeVar, List

T = TypeVar('genotype')

class Evolver(ABC):
    """
    The Evolver class is an abstract base class from which you may derive the
    objects which will comprise your population. The best approach is to use
    multiple inheritance and create an evolvable subclass of whatever it is you
    want to use the GA on.

    The type specified must match the type specified in the first template
    parameter of your GA, otherwise it won't work. You are not limited to basic
    types for your genes, any class may be used, but you will need to provide
    a suitable mutation operator for that class.
    """

    def __init__(self):

        self.GAFitnessScores: List[float] = [] # A list of previous scores
        self.GAProbability: float = 0.0
        self.GAFitness: float = 0.0
        self.GAFixedFitness: float = 0.0
        self.PSOBestSolution: List[T] = []
        self.PSOBestFitness: float = 0.0


    @property
    def GAFitnessScoreAverage(self):
        assert self.GAFitnessScores, 'no fitness score recorded'
        return sum(self.GAFitnessScores) / len(self.GAFitnessScores)

    def StoreFitness(self):
        """
        Stores current fitness, overload this for one way of resetting
        individuals' internal fitness scores each assessment (another way might
        be e.g. to overload Init).

        Note: If you are using only one fitness score per individual you do not
        need to call StoreFitness, the GA will simply get the fitness from the
        fitness function.
        """
        self.GAFitnessScores.append(self.GetFitness())


    @abstractmethod
    def GetGenotype(self) -> List[T]:
        """
        Returns the genotype.
        """
        pass

    @abstractmethod
    def SetGenotype(self, genotype: T):
        """
        Sets the genotype.
        """
        pass


