# from built-in
import pickle
# from third-party
import numpy as np
# from pybeast
from pybeast.paths import DATA_DIR
from pybeast.core.simulation import Simulation
from pybeast.core.agents.animat import Animat
from pybeast.core.utils.vector2D import Vector2D
from pybeast.core.world.world import WORLD_DISP_PARAM

class Braitenberg(Animat):
    """Braitenberg class representing a basic bot with sensors."""

    def Control(self):
        pass

    def __init__(self):
        """Initialize a Braitenberg object."""

        startLocoation = Vector2D(0.5*WORLD_DISP_PARAM.width, 0.5*WORLD_DISP_PARAM.height)

        super().__init__(startLocation = startLocoation, startOrientation = 0.5*np.pi)

        self.controlMax = 0.5
        self.controlMin = 0.3
        self.p = 0.3

        self.controls['left'] = self.controlMax
        self.controls['right'] = self.controlMin

        self.SetMinSpeed(50.0)
        self.SetMaxSpeed(150.0)
        self.SetRadius(10.0)

    def Update(self):

        if np.random.rand() <= self.p:

            if self.controls['left'] == self.controlMax:
                self.controls['left'] = self.controlMin
                self.controls['right'] = self.controlMax
            else:
                self.controls['left'] = self.controlMax
                self.controls['right'] = self.controlMin

        super().Update()

class AnimatTestSimulation2(Simulation):
    """BraitenbergSimulation class representing a simulation with Braitenberg vehicles and dots."""

    def __init__(self):
        """Initialize a BraitenbergSimulation object."""
        super().__init__('AnimatTest2')

        self.whatToLog['Generation'] = self.whatToLog['Assessment'] = self.whatToLog['Update'] = True
        self.whatToSave['Simulation'] = self.whatToSave['Assessment'] = self.whatToSave['Update'] = True

        self.assessments = 5
        self.timeSteps = 100

    def BeginAssessment(self):
        self.theAnimat = Braitenberg()
        self.theWorld.Add(self.theAnimat)
        super().BeginAssessment()

    def CreateDataStructSimulation(self):
        self.data = {}
        self.data['trajectories'] = []

    def CreateDataStructAssessment(self):
        self.x_trajectory = []
        self.y_trajectory = []

    def SaveSimulation(self):
        with open(DATA_DIR / 'animat_test_2.pkl', 'wb') as file:
            pickle.dump(self.data, file)

    def SaveAssessment(self):
        self.data['trajectories'].append(np.vstack((self.x_trajectory, self.y_trajectory)))

    def SaveUpdate(self):
        pos = self.theAnimat.GetLocation()
        self.x_trajectory.append(pos.x)
        self.y_trajectory.append(pos.y)

if __name__ == "__main__":

    simulation = AnimatTestSimulation2()
    simulation.RunSimulation(render=True)

