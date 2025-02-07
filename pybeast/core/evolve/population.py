# from built-in
from abc import ABC, abstractmethod
from copy import deepcopy
from typing import TypeVar, TYPE_CHECKING, Type, Sequence, Mapping, Union
# from third-party
import numpy as np
# from pybeast
from pybeast.core.evolve.geneticalgorithm import GeneticAlgorithm
from pybeast.core.world.worldobject import WorldObject
from pybeast.core.agents.animat import Animat
from pybeast.core.evolve.evolver import Evolver

if TYPE_CHECKING:
    from pybeast.core.world.world import World

FromWorldObject = TypeVar('T', bound=WorldObject)
FromAnimatAndEvolver = TypeVar('T', bound=Union[Animat, Evolver])

class SimObject(ABC):
    """
    An abstract base class for the Population template, allowing populations
    with different templated types to be represented in Simulation.
    """
    def __init__(self):
        pass

    #================================================================================================
    # Are called at the start/end of a run, generation, and assesement
    #================================================================================================

    def BeginAssessment(self):
        pass

    def EndAssessment(self):
        pass

    def BeginGeneration(self):
        pass

    def EndGeneration(self):
        pass

    def BeginRun(self):
        pass

    def EndRun(self):
        pass
    @abstractmethod
    def AddToWorld(self):
        pass

    #================================================================================================
    # Set and get World object
    #================================================================================================

    def GetWorld(self):
        """Returns the world in which the SimObject resides."""
        return self.myWorld

    def SetWorld(self, w: "World"):
        """Sets the world used in AddToWorld."""
        self.myWorld = w

    #================================================================================================
    # Serialise and Save Simulation object
    #================================================================================================

    def Serialise(self):
        pass

    def Unserialise(self, file):
        pass

    def Save(self, fileName):
        """
        Uses the SimObject's Serialise method (selected through polymorphism)
        to stream the object to the specified file.
        :param fileName: The name of the file to save to.
        :return: True if successful.
        """
        try:
            with open(fileName, 'wb') as file:
                self.Serialise(file)
            return True
        except Exception as e:
            print(f"Error saving to file '{fileName}': {e}")
            return False

    def Load(self, fileName):
        """
        Uses the SimObject's Unserialise method (selected through
        polymorphism) to reinstate the object from the specified file.
        :param fileName: The name of the file to load from.
        :return: True if successful.
        """
        try:
            with open(fileName, 'rb') as file:
                self.Unserialise(file)
            return True
        except Exception as e:
            print(f"Error loading file '{fileName}': {e}")
            return False

class Group(SimObject):
    """
    A simple class which creates and maintains a vector of objects of the
    specified type and adds them to the world each round.
    Note that Group is also responsible for deleting the objects it contains,
    if you attempt to delete any of the objects in a Group yourself, there
    will likely be segmentation faults.
    :param _ObjType: The type of objects to create.
    """

    def __init__(self,
        N: int,
        GroupType: FromWorldObject,
        *args: Sequence,
         **kwargs: Mapping):

        self.N = N
        self.Type = GroupType
        # Initialize group members of specified type
        self.members = [self.Type(*args, **kwargs) for _ in range(self.N)]

    def __del__(self):
        """Destructor - deletes all the objects in the group."""
        self.members.clear()

    def AddToWorld(self):
        """Adds the objects in the group to the world."""
        assert hasattr(self, 'myWorld'), "world not set, use 'SimObject.SetWorld' to set it"

        for member in self.members:
            self.myWorld.Add(member)

    def ForEach(self, method: str, *args: Sequence, **kwargs: Mapping):
        """
        Calls the specified member function on each object in the Group.
        """

        return [getattr(member, method)(*args, **kwargs) for member in self.members]

    def EndAssessment(self):

        for members in self.members:
            members.Reset()

    #================================================================================================
    # Serialise
    #================================================================================================

    def Serialise(self, out):
        """
        Serializes the Group to the given output stream.
        """
        # TODO: Implement serialisation in a consistent manner throughout the project
        assert False, 'Not implemented yet'

    def Unserialise(self, inp):
        """
        Unserializes objects from the given input stream and adds them to the group.
        """
        # TODO: Implement serialisation in a consistent manner throughout the project
        assert False, 'Not implemented yet.'



class Population(Group):
    """
    This class is derived from Group and adds a managed GA which is
    automatically run on the whole Population every epoch.

    Attributes:
        GA (GeneticAlgorithm): The genetic algorithm associated with the population.
        teamsize (int): The number of individuals in a team for assessment.
        numClones (int): The number of clones to be made of each individual in each assessment.
        team (List[_Ind]): The current team of individuals.
        current (int): The index of the current individual in the population.
    """

    def __init__(self,
        popSize: int,
        popType: FromAnimatAndEvolver,
        ga: GeneticAlgorithm,
        teamsize: int = -1,
        *args: Sequence,
        **kwargs: Mapping):
        """
        :param N: The size of the population.
        :param popType: Population type. 'popType' is used to init members in the population
        :param ga: The genetic algorithm associated with the population.
        """

        super().__init__(popSize, popType, *args, **kwargs)

        self.GA = ga
        self.GA.SetPopulation(self)

        self.teamsize = teamsize # Decides how many individuals will go into assessments
        self.numClones = 0 # Decides how many clones are made to go into assessment
        self.current = None
        self.team = []

        # Additional arguments
        self.args = args
        self.kwargs = kwargs

    #================================================================================================
    #  Class Interface
    #================================================================================================

    def AddToWorld(self):
        """Adds the members in the population to the world."""

        assert hasattr(self, 'myWorld'), "world not set, use 'SimObject.SetWorld' to set it"

        if self.teamsize == -1:
            for member in self.members:
                self.myWorld.Add(member)
        else:
            for member in self.team:
                self.myWorld.Add(member)

    def Clone(self, member: FromAnimatAndEvolver) -> FromAnimatAndEvolver:
        """
        Used by Population to create a clone of an individual (see Population.BeginAssessment)
        """
        return deepcopy(member)

    def Merge(self, member1: FromAnimatAndEvolver, member2: FromAnimatAndEvolver) -> FromAnimatAndEvolver:
        """
        Merges two individuals such that the resulting individual's fitness scores
        will contain all the scores of both individuals.
        (see Population.EndAssessment)
        """
        member1.GAFitnessScores.append(member2.GetFitness())
        del member2

        return member1

    def AverageFitnessScoreOfMembers(self):
        """
        Calculates average fitness across all members in the population
        """
        return [member.GAFitnessScoreAverage for member in self.members]

    #================================================================================================
    # Update methods during simulation
    #================================================================================================

    def BeginRun(self):
        """
        This method is called at the beginning of the run and ensures that the
        contents of the population have been reset.
        """
        # Clear members in population
        self.members.clear()
        # Regenerating new elements in the population
        self.members = [self.Type(*self.args, **self.kwargs) for _ in range(self.N)]

    def BeginGeneration(self):
        """Called at the beginning of the generation."""
        self.current = iter(self.members)

    def BeginAssessment(self):
        """
        Called at the beginning of the assessment.
        Sets up teams if required and creates clones of individuals for assessment.
        """

        if self.teamsize != -1:
            self.team.clear()

            # In each assessment we select 'self.teamSize' members of to population to be assessed
            # Members are selected sequentially from the 'self.members' list, if we reach the end of
            # the list we reset the iterator to the start
            if self.current is None:
                self.current = iter(self.members)

            for _ in range(self.teamsize):
                try:
                    self.team.append(next(self.current))
                except StopIteration:
                    self.current = iter(self.members)
                    self.team.append(next(self.current))

            # Add additional clones if desired to increase the team size
            for _ in range(self.numClones):
                self.team.extend([self.Clone(member) for member in self.team])

    def EndAssessment(self):
        """
        Called at the end of the assessment. Stores fitness scores for each individual.
        """

        if self.teamsize != -1:
            for member in self.team:
                member.StoreFitness()
                member.Reset()
        else:
            for member in self.members:
                member.StoreFitness()
                member.Reset()

    def EndGeneration(self):
        """
        Called at the end of generation after all assessments. Generates the new generation based on the performance
         of the members in current generation using the genetic algorithm.
        """
        self.GA.Generate()
        # Clear old population
        self.members.clear()
        # Insert new population
        self.members.extend(self.GA.outputPopulation)

#================================================================================================
# Getter and Setter
#================================================================================================

    def SetTeamSize(self, n: int):
        self.teamsize = n

    def SetClones(self, n: int):
        self.numClones = n

    def GetTeam(self):
        return self.team

#================================================================================================
# Serialise
#================================================================================================

    def Serialise(self, out_stream):

        # TODO: Implement in a cosistent manner throughout the project
        assert False, "Not implemented yet."

        # out_stream.write(f"Population_{type(_Ind).__name__}\n")
        # self.GA.Serialise(out_stream)
        # out_stream.write(f"{len(self)}\n")
        # for ind in self:
        #     out_stream.write(f"{ind.GetGenotype()}\n")

    def Unserialise(self, in_stream):

        # TODO: Implement in a cosistent manner throughout the project
        assert False, "Not implemented yet."

        # name = in_stream.readline().strip()
        # if name != f"Population_{type(_Ind).__name__}":
        #     raise SerialException(SERIAL_ERROR_WRONG_TYPE, name,
        #                           f"This object is type Population_{type(_Ind).__name__}")
        #
        # self.GA.Unserialise(in_stream)
        # s = int(in_stream.readline().strip())
        #
        # self.clear()
        # for _ in range(s):
        #     g = eval(in_stream.readline().strip())  # Assuming genotype is serializable
        #     ind = _Ind()
        #     ind.SetGenotype(g)
        #     self.append(ind)
