"""
BEAST application module.

This module initializes and runs the BEAST application.
"""
# from built-in
from typing import Optional
# from third-party
import wx
# from pybeast
from pybeast.gui.beastframe import BeastFrame
from pybeast.core.simulation import Simulation

class BeastApp(wx.App):
    """
    BeastApp class.

    The BEAST application class.
    """
    def __init__(self, mySimulation: Optional[Simulation] = None):

        self.mySimulation = mySimulation
        super().__init__(False)

    def OnInit(self):
        """
        Initialize the BEAST application.

        Returns:
            bool: True if initialization is successful, False otherwise.

        """
        # Create the main frame window
        self.beastFrame = BeastFrame(None,
                                     "BEAST - Bioinspired Evolutionary Agent Simulation Toolkit",
                                      mySimulation = self.mySimulation
        )

        # Show the frame
        self.beastFrame.Show(True)
        self.SetTopWindow(self.beastFrame)

        return True

if __name__== '__main__':

    app = BeastApp()
    app.MainLoop()


