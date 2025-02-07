import threading
import time

import wx

from pybeast.gui.worldglcanvas import WorldGLCanvas

class MinimalBeastApp(wx.App):

    def __init__(self, simulation):

        self.simulation = simulation
        super().__init__(False)

    def OnInit(self):
        self.frame = MinimalBeastFrame(self.simulation)
        self.frame.Show(True)
        self.SetTopWindow(self.frame)

        return True

class MinimalBeastFrame(wx.Frame):

    def __init__(self, simulation):

        super().__init__(None, -1, 'BEAST', wx.Point(50, 50), wx.Size(808, 681))
        self.simulation = simulation
        self.fps = 33

        # Call a method after the main event loop starts
        return

    def StartSimulation(self):

        time.sleep(0.5)
        #event = wx.SizeEvent(self.GetClientSize())
        #self.worldCanvas.OnSize(event)

        # Run simulation in separate thread to avoid GUI freeze
        thread = threading.Thread(target=self.RunSimulation)
        thread.daemon = True
        thread.start()

    def RunSimulation(self):
        """
        Runs simulation
        """
        # Take ownership of context can display empty world
        self.worldCanvas = WorldGLCanvas(self, self.GetClientSize(), self.simulation.theWorld)
        time.sleep(0.5)

        self.simulation.BeginSimulation()

        # This is the rendering loop: Update returns False until all runs are completed. A run consists of
        # 'self.m_pSimulation.generations' numbers of generations and each generation consists
        # of 'self.m_pSimulation.assessments' assessments, and each assessment runs for 'self.m_pSimulation.timeSteps'
        while True:
            startTime = time.time()

            # Update simulation
            complete = self.simulation.Update()
            # Render the updated world
            wx.CallAfter(self.worldCanvas.Display)
            # Sleep if rendering faster than desired frame rate
            sleepTime = max(0, 1.0 / self.fps - (time.time() - startTime))
            time.sleep(sleepTime)

            if complete:
                break

            self.worldCanvas.SetCurrent(self.worldCanvas.context)

        return


