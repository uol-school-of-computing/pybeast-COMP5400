# from built-in
import copy
import random
from unittest.mock import patch
# from third-party
import numpy as np
# from built-in
from pybeast.demos.evo_mouse import EvoMouse
from pybeast.core.evolve.geneticalgorithm import GeneticAlgorithm, GAFitnessMethodType, GAFitnessFixType, \
    GASelectionType, GAFltParamDefault
from pybeast.core.evolve.population import Population

class TestEvoMouse(EvoMouse):

    def Reset(self):
        self.cheesesFound = 0

    def GetFitness(self) -> float:
        return self.cheesesFound


def init_population(popSize, teamsize = -1):

    fitnessFix = random.choice(list(GAFitnessFixType.__dict__.values()))
    selection = random.choice(list(GASelectionType.__dict__.values()))
    # TODO: Implement random options
    GA = GeneticAlgorithm(fitnessFix = fitnessFix, selection=selection)
    GA.fltParams.GA_EXPONENT = 2.5 * random.random() + 0.5
    population = Population(popSize, TestEvoMouse, GA, teamsize=teamsize)

    population.BeginGeneration()

    if teamsize == -1:
        population.BeginAssessment()

    return population

def test_assign_fitness():

    def GetFitness(cheesesFound, distanceTravelled):
        return cheesesFound/distanceTravelled

    for _ in range(1000):

        popSize = 30
        population = init_population(popSize)

        # Instead of actually simulating, we assign random fitness values to members in the population
        fitness_arr = np.random.randint(0, 5, size = popSize)
        for i, member in enumerate(population.members):
            member.cheesesFound = fitness_arr[i]
        # Check that assignment works
        assert np.allclose(fitness_arr, [member.GetFitness() for member in population.members])

        # At the end of each assement fitness scores are transfered to GAFitnessScores
        population.EndAssessment()
        # Check that assignment works
        assert np.allclose(fitness_arr,  [member.GAFitnessScores[0] for member in population.members])

        # Check that genetic algorithm returns the correct fitness
        for i, member in enumerate(population.members):

            fitness = population.GA.GetFitness(member)
            assert population.GA.GetFitness(member) == fitness_arr[i]

    print("Passed 'test_genetic_algorithm.test_assign_fitness'!")


def test_calc_stats():

    for _ in range(1000):

        popSize = 30
        population = init_population(popSize)
        fitness_arr = np.random.randint(0, 5, size = popSize)

        for i, member in enumerate(population.members):
            member.cheesesFound = fitness_arr[i]

        population.EndAssessment()
        population.GA.CalcStats()

        bestFitness = fitness_arr.max()
        worstFitness = fitness_arr.min()
        totalFitness = fitness_arr.sum()

        bestCurrentGenome = population.members[fitness_arr.argmax()].GetGenotype()

        assert population.GA.bestFitness == bestFitness
        assert population.GA.worstFitness == worstFitness
        assert population.GA.totalFitness == totalFitness
        assert np.allclose(population.GA.bestCurrentGenome, bestCurrentGenome)

    print("Passed 'test_genetic_algorithm.test_calc_stats'!")

def test_setup():

    for _ in range(1000):

        popSize = 30
        population = init_population(popSize)
        fitness_arr = np.random.randint(0, 5, size = popSize)

        for i, member in enumerate(population.members):
            member.cheesesFound = fitness_arr[i]

        population.EndAssessment()
        population.GA.CalcStats()
        population.GA.Setup()

        if population.GA.fitnessFix == GAFitnessFixType.GA_IGNORE:
            fixed_fitness_arr = fitness_arr
        elif population.GA.fitnessFix == GAFitnessFixType.GA_FIX:
            fixed_fitness_arr = fitness_arr - fitness_arr.min()
        elif population.GA.fitnessFix == GAFitnessFixType.GA_CLAMP:
            fixed_fitness_arr = fitness_arr
            fixed_fitness_arr[fitness_arr < 0.0] = 0.0

        sorted_fixed_fitness = np.sort(fixed_fitness_arr)[::-1]
        total_fitness = sorted_fixed_fitness.sum()

        # Check if fixed fitness calculation and sorting
        assert np.allclose([member.GAFixedFitness for member in population.members], sorted_fixed_fitness)

        if population.GA.selection == GASelectionType.GA_ROULETTE:
            propability_arr = (sorted_fixed_fitness / total_fitness) ** population.GA.fltParams.GA_EXPONENT
        elif population.GA.selection == GASelectionType.GA_RANK:
            rank_arr = np.arange(popSize)
            propability_arr = (1.0 - rank_arr / (popSize - 1)) ** GAFltParamDefault.GA_EXPONENT
        elif population.GA.selection == GASelectionType.GA_TOURNAMENT:
            pass

        if population.GA.selection in [GASelectionType.GA_ROULETTE, GASelectionType.GA_RANK]:
            propability_arr /= np.sum(propability_arr)
            # Check propabilities are calculated as expected
            assert np.allclose([member.GAProbability for member in population.members], propability_arr)
            # Check that propabilities sum up to one
            assert np.isclose(np.sum(propability_arr), 1.0)

    print("Passed 'test_genetic_algorithm.test_setup'!")

def test_crossover():

    for _ in range(1000):

        popSize = 30
        population = init_population(popSize)

        member1, member2 = random.choices(population.members, k=2)
        mum, dad = member1.GetGenotype(), member2.GetGenotype()
        assert len(mum) == len(dad)
        crossover_point = random.randint(0, len(mum))

        with patch('random.randint', return_value=crossover_point):
            # Generate new population
            child1, child2 = population.GA.CrossoverGenotypes(mum, dad)

        assert np.array_equal(child1, np.concatenate((mum[:crossover_point], dad[crossover_point:])))
        assert np.array_equal(child2, np.concatenate((dad[:crossover_point], mum[crossover_point:])))

    print("Passed 'test_genetic_algorithm.test_crossover'!")

def test_mutation():

    for _ in range(1000):

        popSize = 30
        population = init_population(popSize)

        member1 = random.choices(population.members, k=1)[0]
        genom_before_mutation = member1.GetGenotype()

        random_arr = np.random.rand(popSize)

        with patch('random.random', side_effect=random_arr):
            # Generate new population
            genom_after_mutation = genom_before_mutation.copy()
            population.GA.MutateGenotype(genom_after_mutation)

        for i, (chromo_before, chromo_after) in enumerate(zip(genom_before_mutation, genom_after_mutation)):
            if random_arr[i] < population.GA.mutation:
                assert chromo_before != chromo_after
            else:
                assert chromo_before == chromo_after

    print("Passed 'test_genetic_algorithm.mutation'!")

def test_generate():

    for _ in range(1000):

        popSize = 30
        population = init_population(popSize)
        fitness_arr = np.random.randint(0, 5, size = popSize)

        for i, member in enumerate(population.members):
            member.cheesesFound = fitness_arr[i]

        # Sort population from fittest to weakest and assign probabilities
        population.EndAssessment()
        population.GA.CalcStats()
        population.GA.Setup()

        # Generate new population
        population.GA.Generate()

        # Check culling
        assert len(population.members) == popSize - population.GA.culling

        # Check elitism
        elitism = population.GA.elitism
        if elitism > 0:
            for member1, member2 in zip(population.members[:elitism], population.GA.outputPopulation[:elitism]):
                assert member1.GetGenotype() == member2.GetGenotype()
                assert member1 is not member2

    print("Passed 'test_genetic_algorithm.test_generate'!")

def test_team_assignment():

    for i in range(int(1e3)):

        popSize = 2 * random.randint(5, 50)
        divisors = []

        for i in range(2, popSize):
            if popSize % i == 0:
                divisors.append(i)

        teamsize = random.choice(divisors)
        assessments = popSize // teamsize

        population = init_population(popSize, teamsize)

        k = 0

        for _ in range(assessments):
            population.BeginAssessment()
            for i in range(teamsize):
                assert population.members[k] is population.team[i]
                k += 1

    print("Passed 'test_genetic_algorithm.test_team_assignment'!")

def test_team_fitness():

    for i in range(int(1e3)):

        popSize = 2 * random.randint(5, 50)
        divisors = []

        for i in range(2, popSize):
            if popSize % i == 0:
                divisors.append(i)

        teamsize = random.choice(divisors)
        assessments = popSize // teamsize

        population = init_population(popSize, teamsize)

        k = 0

        fittness_arr = []

        for _ in range(assessments):
            population.BeginAssessment()
            for member in population.team:
                cheese = float(np.random.randint(0, 5))
                member.cheesesFound = cheese
                fittness_arr.append(cheese)
                k += 1
            population.EndAssessment()

        assert np.allclose(fittness_arr, [member.GAFitnessScores[0] for member in population.members])

    print("Passed 'test_genetic_algorithm.test_team_fitness'!")

if __name__ == '__main__':

    test_assign_fitness()
    test_calc_stats()
    test_setup()
    test_crossover()
    test_mutation()
    test_generate()
    test_team_assignment()
    test_team_fitness()