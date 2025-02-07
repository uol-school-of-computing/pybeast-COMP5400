# from pybeast
from test_agents import *
from test_evolver import *
from test_FFN import *
from test_genetic_algorithm import *
from test_sensors import *

if __name__ == '__main__':

    print('Start tests: \n')

    test_InitAnimat()
    test_InitBrainAnimat()
    test_set_genome()
    test_fire()
    test_set_config()
    test_assign_fitness()
    test_calc_stats()
    test_setup()
    test_crossover()
    test_mutation()
    test_generate()
    test_team_assignment()
    test_team_fitness()
    test_NearestAngle()
    test_Proximity()

    print('\n Passed all tests!')