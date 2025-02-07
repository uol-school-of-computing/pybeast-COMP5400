"""
simulation.py
author: David Gordon (migrated from C++ to python by Lukas Deutz)

The Simulation class is a framework of classes providing the facilities for implementing a range of different types of
simulation. SimObject is an interface class for the Group class, which simply adds objects to the Simulation, and the
Population class which handles GA functionality and the insertion of groups of Animats (or other evolvable WorldObjects)
into the World.
"""
# from built-in
import io
from typing import  TypeVar
from abc import ABC
from types import SimpleNamespace
import pickle
import sys
import time
import logging
import multiprocessing

import wx
# third-party
from OpenGL.GL import glFinish

# from pybeast
from pybeast.core.world.world import World
from pybeast.core.evolve.population import SimObject
from pybeast.core.profiler import Profiler

T = TypeVar('T', bound = SimObject)

PRINT_TYPE_STATUS = SimpleNamespace(**{
    'SIM_PRINT_STATUS': 0,
    'SIM_PRINT_ASSESSMENT': 1,
    'SIM_PRINT_RUN': 2,
    'SIM_PRINT_COMPLETE': 3,
})

class Simulation(ABC):
    """
    The basic Simulation framework which must be derived to set up simulations.
    This class cannot itself be instantiated. To derive your own Simulation:
    - Create a new class, publicly derived from Simulation.
    - Specify your simulation contents (e.g. Group and Population classes) as
    member data.
    - Create a public constructor which initializes the member data, then adds
    each object using Simulation::Add.
    - Perform any setup of the World, the Simulation, or the contents in the
    constructor.
    - If you need to perform actions every epoch, override the virtual method,
    Init.
    """
    def __init__(self, name):

        self.theWorld = World(self)
        self.contents = {}
        self.Runs = 1
        self.generations = 1
        self.assessments = 1
        self.timeSteps = 1000
        self.timeIncrement = 1
        self.sleepBetweenLogs = 0.0
        self.logger = logging.getLogger(name)
        self.InitLogger()

        self.profile = False
        self.profiler = Profiler()

        self.whatToLog = {'Simulation': True, 'Run': True, 'Generation': False, 'Assessment': False, 'Update': False}
        self.whatToSave = {'Simulation': False, 'Run': False, 'Generation': False, 'Assessment': False, 'Update': False}

        self.hasBeenLoaded = False

    def InitLogger(self):
        """
        Adds handler that logs to python console
        """
        # This line is needed to avoid multiple handlers being added in jupyter notebook if cells a rerun
        self.logger.handlers = []
        self.logger.setLevel(logging.INFO)
        consoleHandler = logging.StreamHandler(sys.stdout)
        consoleHandler.setLevel(logging.INFO)
        consoleHandler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        self.logger.addHandler(consoleHandler)

    def ToString(self, s: int) -> str:
        """
        Reports a few details about the current state of the simulation.

        Parameters:
            s (SimPrintStyleType): The style of output.

        Returns:
            str: The output string.
        """
        out = io.StringIO()

        if s == PRINT_TYPE_STATUS.SIM_PRINT_STATUS:
            if self.complete:
                return "Simulation complete"
            else:
                if self.Run != 1:
                    out.write(f"Run: {self.Run + 1}/{self.Run}, ")
                out.write(f"Generation: {self.generation + 1}")
                if self.generations != 0:
                    out.write(f"/{self.generations}, ")
                if self.assessments != 1:
                    out.write(f"Assessment: {self.assessment + 1}/{self.assessments}, ")
                out.write(f"Time step: {self.timeStep + 1}/{self.timeSteps}")

        elif s == PRINT_TYPE_STATUS.SIM_PRINT_ASSESSMENT:
            pass

        elif s == PRINT_TYPE_STATUS.SIM_PRINT_GENERATION:
            for sim_object in self.contents.values():
                out.write(sim_object.ToString())

        elif s == PRINT_TYPE_STATUS.SIM_PRINT_RUN:
            pass

        elif s == PRINT_TYPE_STATUS.SIM_PRINT_COMPLETE:
            pass

        return out.getvalue()

    #================================================================================================
    # Class interface
    #================================================================================================

    def RunSimulation(self, render = False, parallelize = False):

        if render:
            from pybeast.beast import BeastApp
            app = BeastApp(self)
            app.MainLoop()
        else:
            self.RunSimulationWithoutRendering(parallelize = parallelize)

    def RunSimulationWithoutRendering(self, parallelize):

        if self.profile:
            self.profiler.Start()

        self.Init()
        self.BeginSimulation()

        while True:
            complete = self.Update()
            if complete:
                break

    def RunRunParallel(self):
        #TODO
        pass

    def CleanUp(self):
        """
        Safely clean up all wxPython objects and ensure the application shuts down cleanly.
        """
        app = wx.GetApp()

        if app:
            # Get all top-level windows and destroy them
            for window in wx.GetTopLevelWindows():
                if window:
                    window.Close(True)  # Close the window
                    window.Destroy()  # Destroy the window

            # If the main loop is running, exit it
            if app.IsMainLoopRunning():
                app.ExitMainLoop()

            # Explicitly delete the app object
            del app
            wx.GetApp().Destroy()

    def Add(self, name: str, pop: T):
        """
        Adds a Population, Group or other SimObject to the world.
        """
        self.contents[name] = pop

    def Init(self):
        """
        Initializes the simulation by setting the current run to 0, setting the
        complete flag to False, assigning each SimObject a pointer to theWorld,
        and then starting the run.
        """
        # Tell every simulation object about the world they live in
        for simObject in self.contents.values():
            simObject.SetWorld(self.theWorld)

    def Display(self):

        self.theWorld.Display()
        glFinish()
        self.SwapBuffers()


    def Update(self) -> bool:
        """
        Updates the World once and checks if the time limit has been reached.
        If the time limit has been reached, EndAssessment is called.

        Returns:
            bool: False if the simulation is not complete, True otherwise.
        """
        if self.profile:
            self.profiler.functionsToProfile['Simulation.Update']['count'] += 1
            startTime = time.time()

        self.theWorld.Update()
        self.timeStep += self.timeIncrement

        if self.whatToSave['Update']:
            self.SaveUpdate()

        if self.whatToLog['Update']:
            self.LogUpdate()

        if self.profile:
            endTime = time.time()
            self.profiler.functionsToProfile['Simulation.Update']['times'].append(endTime - startTime)

        if self.timeStep == self.timeSteps:
            self.EndAssessment()

        return self.complete

    def BeginSimulation(self):
        """
        This method is called at the beginning of the simulation. If you want to override this method, ensure
        that 'super().BeginSimulation' is called at the end of your overridden version.
        """
        if self.whatToSave['Simulation']:
            self.CreateDataStructSimulation()

        if self.whatToLog['Simulation']:
            self.LogBeginSimulation()
            time.sleep(self.sleepBetweenLogs)

        self.complete = False
        self.Run = 0
        self.BeginRun()

    def ResumeSimulation(self):

        if self.whatToSave['Simulation']:
            self.CreateDataStructSimulation()

        if self.whatToLog['Simulation']:
            self.LogResumeSimulation()
            time.sleep(self.sleepBetweenLogs)

    def  BeginRun(self):
        """
        This method is called at the beginning of every run. If you want to override this method, ensure
        that 'super().BeginRun' is called at the end of your overridden version.
        """
        if self.whatToSave['Run']:
            self.CreateDataStructRun()

        if self.whatToLog['Run']:
            self.LogBeginRun()
            time.sleep(self.sleepBetweenLogs)

        self.generation = 0

        # Call BeginRun on every simulation object
        for simObject in self.contents.values():
            simObject.BeginRun()

        self.BeginGeneration()

    def BeginGeneration(self):
        """
        This method is called at the beginning of every generation. If you want to override this method, ensure
        that 'super().BeginGeneration' is called at the end of your overridden version.
        """

        if self.whatToSave['Generation']:
            self.CreateDataStructGeneration()

        if self.whatToLog['Generation']:
            self.LogBeginGeneration()
            time.sleep(0.5)

        self.assessment = 0

        # Call BeginGeneration on every simulation object
        for simObject in self.contents.values():
            simObject.BeginGeneration()

        self.BeginAssessment()

    def BeginAssessment(self):
        """
        This method is called at the beginning of every assessment. If you want to override this method, ensure
        that 'super().BeginAssessment' is called at the end of your overridden version.
        """

        if self.whatToSave['Assessment']:
            self.CreateDataStructAssessment()

        if self.whatToLog['Assessment']:
            self.LogBeginAssessment()
            time.sleep(self.sleepBetweenLogs)

        self.timeStep = 0

        for simObject in self.contents.values():
            simObject.BeginAssessment()
            simObject.AddToWorld()

        self.theWorld.Init()

        return

    def EndSimulation(self):
        """
        Ends simulation after last run is completed
        """
        if self.whatToSave['Simulation']:
            self.SaveSimulation()

        # Log end of simulation
        if self.whatToLog['Simulation']:
            self.LogEndSimulation()
            time.sleep(self.sleepBetweenLogs)

        self.theWorld.CleanUp()
        self.complete = True

        return


    def EndRun(self):
        """
        This method is called at the end of every run and is responsible for either stopping the simulation
        if the maximum number of runs has been reached. If you want to override this method, ensure that Simulation::EndRun is called at the end of your overridden version.
        """

        if self.whatToSave['Run']:
            self.SaveRun()

        # Log end of Run
        if self.whatToLog['Run']:
            self.LogEndRun()
            time.sleep(self.sleepBetweenLogs)

        # Call EndRun on every simulation object
        for simObject in self.contents.values():
            simObject.EndRun()

        self.Run += 1

        if self.Run == self.Runs:
            self.EndSimulation()
        else:
            self.BeginRun()

    def EndGeneration(self):
        """
        This method is called at the end of every generation. If you want to override this method,
        ensure that super().EndGeneration is called at the end of your overridden version.
        """
        if self.profile:
            self.profiler.functionsToProfile['Simulation.EndGeneration']['count'] += 1
            startTime = time.time()

        if self.whatToSave['Generation']:
            self.SaveGeneration()

        # Log end of generation
        if self.whatToLog['Generation']:
            self.LogEndGeneration()
            time.sleep(self.sleepBetweenLogs)

        # Call EndGeneration on every simulation object
        for sim_object in self.contents.values():
            sim_object.EndGeneration()

        self.generation +=1

        if self.profile:
            endTime = time.time()
            self.profiler.functionsToProfile['Simulation.EndGeneration']['times'].append(endTime - startTime)

        if self.generation == self.generations:
            self.EndRun()
        else:
            self.BeginGeneration()




    def EndAssessment(self):
        """
        This method is called at the end of every assessment. If you want to override this method, ensure that
        super().EndAssessment is called at the end of your overridden version.
        """
        # Call EndAssessment on every simulation object
        for simObject in self.contents.values():
            simObject.EndAssessment()

        if self.whatToSave['Assessment']:
            self.SaveAssessment()

        if self.whatToLog['Assessment']:
            self.LogEndAssessment()
            time.sleep(self.sleepBetweenLogs)

        self.theWorld.CleanUp()

        self.assessment += 1

        if self.assessment == self.assessments:
            self.EndGeneration()
        else:
            self.BeginAssessment()

    #================================================================================================
    # Reset the simulation/runs/generations/assessements
    #================================================================================================

    def ResetRun(self):
        """
        Sets the number of runs for this simulation. Has no effect if the number of generations has not been specified
        using SetGenerations.
        """
        self.theWorld.CleanUp()
        self.Run -= 1
        self.BeginRun()

    def ResetGeneration(self):
        """
        This method is called when the GUI needs to break the current generation
        and start again from the beginning of that generation.
        """
        self.theWorld.CleanUp()
        self.BeginGeneration()

    def ResetAssessment(self):
        """
        This method is called when the GUI needs to break the current assessment
        and start again from the beginning of that assessment.
        """
        self.theWorld.CleanUp()
        self.BeginAssessment()

    #================================================================================================
    # Logger methods which should can be overloaded to provide customized additional info.
    #================================================================================================

    def LogBeginSimulation(self):
        """
        Logs start of the simulation
        """
        self.logger.info(f'Start simulation: Perform {self.Runs} runs, with {self.generations} generations per run, '
                         f'with {self.assessments} assessments per generation, and {self.timeSteps} time steps per assessment.')



    def LogResumeSimulation(self):
        """
        Logs resume loaded simulation
        """
        self.logger.info(f'Resumed simulation with {self.Runs} runs, with {self.generations} generations per run, '
                         f'with {self.assessments} assessments per generation, and {self.timeSteps} time steps per assessment.')
        self.logger.info(f'Current run: {self.Run}, generation: {self.generation}.')


    def LogEndSimulation(self):
        """
        Logs end of the simulation
        """
        self.logger.info(f'Successfully finished simulation')

    def LogBeginRun(self):
        """
        Logs start of a run
        """
        self.logger.info(f'Start run {self.Run + 1} out of {self.Runs} runs')

    def LogEndRun(self):
        """
        Logs end of a run
        """
        self.logger.info(f'Successfully completed run {self.Run+1}')

    def LogBeginGeneration(self):
        """
        Logs start of a generation
        """
        self.logger.info(f'Start generation {self.generation + 1} out of {self.generations} generations')


    def LogEndGeneration(self):
        """
        Logs end of a generation
        """
        self.logger.info(f'Successfully completed generation {self.generation + 1}')

    def LogBeginAssessment(self):
        """
        Logs start of a assessment
        """
        self.logger.info(f'Start assessment {self.assessment + 1} out of {self.assessments} assessments')


    def LogEndAssessment(self):
        """
        Logs end of a assessment
        """
        self.logger.info(f'Successfully completed assessment {self.assessment + 1}')

    def LogUpdate(self):
        """
        Logs end of a update step
        """
        self.logger.info(f'Completed time step {self.timeStep} out of {self.timeSteps}')

    #================================================================================================
    # Save simulation
    #================================================================================================

    def CreateDataStructSimulation(self):
        """
        Creates data struct to buffer simulation results. Data struct can be a file
        """

        pass

    def CreateDataStructRun(self):
        """
        Creates data struct to buffer simulation results. Data struct can be a file
        """

        pass

    def CreateDataStructGeneration(self):
        """
        Creates data struct to buffer simulation results. Data struct can be a file
        """

        pass

    def CreateDataStructAssessment(self):
        """
        Creates data struct to buffer simulation results. Data struct can be a file
        """

        pass

    def SaveSimulation(self):
        """
        Save simulation
        """
        pass

    def SaveRun(self):
        """
        Is called in 'self.EndRun' at the end of each run
        """
        pass

    def SaveGeneration(self):
        """
        Is called in 'self.EndGeneration' at the end of each generation
        """
        pass

    def SaveAssessment(self):
        """
        Is called in 'self.EndAssessment' at the end of each assessment
        """

        pass

    def SaveUpdate(self):
        """
        Is called in 'self.Update' at the end of each time step
        """

        pass

    def SaveContent(self, filepath: str, name: str):

        assert name in self.contents

    #================================================================================================
    # Getter and Setter
    #================================================================================================

    def SetRuns(self, r: int):
        """
        Sets the number of generations per run, if unset generations are unlimited.
        """
        self.Runs = r

    def SetGenerations(self, g: int):
        """
        Sets the number of generations per run, if unset generations are unlimited.
        """
        self.generations = g

    def SetAssessments(self, a):
        """Sets the number of assessments per generation, default is one."""
        self.assessments = a

    def SetTimeSteps(self, t):
        """Sets the number of time steps per assessment, default is 1000."""
        self.timeSteps = t

    def SetLogStream(self, o):
        """
        Sets the output log stream.
        """
        self.logStream = o
        self.theWorld.SetLogStream(o)

    def HasSimObject(self, name):
        """Checks if the specified simulation object is in the simulation."""
        return name in self.contents

    def GetSimObject(self, name: str):
        """Gets the specified simulation object."""
        return self.contents[name]

    def GetRun(self):
        """Gets the current run."""
        return self.Run

    def GetGeneration(self):
        """Gets the current generation."""
        return self.generation

    def GetAssessment(self):
        """Gets the current assessment."""
        return self.assessment

    def GetTimeStep(self):
        """Gets the current timestep."""
        return self.timeStep

    def GetTotalRuns(self):
        """Gets the total runs."""
        return self.Run

    def GetTotalGenerations(self):
        """Gets the total generations."""
        return self.generations

    def GetTotalAssessments(self):
        """Gets the total assessments."""
        return self.assessments

    def GetLogger(self):
        """Gets the log stream."""
        return self.logger

    def GetWorld(self):
        """Gets the World object for this simulation."""
        return self.theWorld

    def GetContents(self):
        """Gets a constant reference to the contents."""
        return self.contents

    #================================================================================================
    # Serialize
    #================================================================================================

    def Serialize(self, filepath):
        """
        Serialize simulation object to file
        """
        with open(filepath, 'wb') as f:
            pickle.dump(self, f)
