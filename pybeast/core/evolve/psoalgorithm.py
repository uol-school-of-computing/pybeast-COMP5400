import random
from typing import TypeVar, List

# Define type variable for generic type EVO
EVO = TypeVar('EVO')

from geneticalgorithm import GeneticAlgorithm
class PSOAlgorithm(GeneticAlgorithm):
    def __init__(self):
        super().__init__()

    def generate(self):
        self.calc_stats()
        self.setup()

        # Ought to be an STL transform
        for i in range(len(self.population)):
            self.output_population.Append(self.fly(self.population[i]))

    def fly(self, e: EVO) -> EVO:
        if not e.PSOBestSolution or e.GAFixedFitness > e.PSOBestFitness:
            e.PSOBestSolution = list(e.GetGenotype())
            e.PSOBestFitness = e.GAFixedFitness

        new_solution = []
        curr_solution = list(e.GetGenotype())

        for curr, p_best, g_best in zip(curr_solution, e.PSOBestSolution, self.best_current_genome):
            new_solution.append(curr + random.uniform(0, 2) * (p_best - curr) + random.uniform(0, 2) * (g_best - curr))

        new_evo = EVO()
        new_evo.SetGenotype(new_solution)
        new_evo.PSOBestSolution = e.PSOBestSolution
        new_evo.PSOBestFitness = e.PSOBestFitness

        return new_evo
