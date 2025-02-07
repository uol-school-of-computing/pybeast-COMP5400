# from built-in
import random
# from third-party
import numpy as np
# from pybeast
from pybeast.core.world.world import WORLD_DISP_PARAM
from pybeast.core.utils.vector2D import Vector2D
from pybeast.core.agents.animat import  Animat
from pybeast.core.agents.neuralanimat import FFNAnimat, DNNAnimat, EvoFFNAnimat, EvoDNNAnimat

def test_InitAnimat():

    # Default initialization
    animat = Animat()
    animat.Init()

    # With start location
    x = WORLD_DISP_PARAM.width * random.random()
    y = WORLD_DISP_PARAM.height * random.random()
    startLocation = Vector2D(x, y)
    animat = Animat(startLocation=startLocation)
    animat.Init()
    assert animat.startLocation == startLocation
    assert animat.location == startLocation
    animat.__repr__()

    # With start orientation
    startOrientation = 2.0 * np.pi *random.random()
    animat = Animat(startOrientation=startOrientation)
    animat.Init()
    assert animat.startOrientation == startOrientation
    assert animat.orientation == startOrientation
    animat.__repr__()

    # With start velocity
    v_x = random.random()
    v_y = random.random()
    startVelocity = Vector2D(v_x, v_y)
    animat = Animat(startVelocity=startVelocity)
    animat.Init()
    assert animat.startVelocity == startVelocity
    assert animat.velocity == startVelocity
    animat.__repr__()

    animat = Animat(startLocation=startLocation, startOrientation=startOrientation, startVelocity=startVelocity)
    animat.Init()
    assert animat.startLocation == startLocation
    assert animat.startOrientation == startOrientation
    assert animat.startVelocity == startVelocity
    assert animat.location == startLocation
    assert animat.orientation == startOrientation
    assert animat.velocity == startVelocity

    #Test random initialization
    animat = Animat()
    animat.Init()

    print("Passed 'test_InitAnimat'!")

    return

def test_InitBrainAnimat():

    ffnAnimat = FFNAnimat()
    ddnAnimat = DNNAnimat()
    evoFFNAnimat = EvoFFNAnimat()
    evoDNNAnimat = EvoDNNAnimat()

    ffnAnimat.Init()
    ddnAnimat.Init()
    evoFFNAnimat.Init()
    evoDNNAnimat.Init()

    print("Passed 'test_agents.test_InitBrainAnimat'!")



if __name__ == '__main__':

    test_InitAnimat()
    test_InitBrainAnimat()





