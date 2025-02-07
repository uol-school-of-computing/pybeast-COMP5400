"""
File: animatmonitor.py
Authors: Tom Carden, David Gordon
"""
# Built-in
from typing import List

# Third-party
from OpenGL.GL import *

# Beast
from pybeast.core.agents.animat import Animat
from pybeast.core.utils.colours import ColourPalette, ColourType

MONITOR_BARHEIGHT = 25

class AnimatMonitor():
    """
    AnimatMonitor class for monitoring animats in the world.
    """
    def __init__(self, animats: List[Animat]):

        self.animats = animats

        self.visible = True
        self.widthSoFar = 0
        self.heightSoFar = 0

    def Display(self):
        """
        Displays the AnimatMonitor if it is visible.

        This method resets the widthSoFar and heightSoFar variables to 0,
        and then iterates over each Animat object in the AnimatMonitor.
        For each Animat, it calls the DrawBars method to draw the bars
        representing the Animat's attributes.
        """
        if self.visible:
            self.widthSoFar = self.heightSoFar = 0

            for animate in self.animats:
                self.DrawBars(animate)

    def DrawBars(self, animat: Animat):
        """
        Draws bars representing attributes of the given Animat. This method draws bars representing attributes of
        the given Animat on the monitor.

        :param animat: The Animat object for which bars are drawn.

        """
        numBars = 2  # already counted motors

        # Set line width
        glLineWidth(4.0)

        # Push matrix
        glPushMatrix()

        # Draw left motor
        glBegin(GL_LINE_STRIP)

        glColor4fv(ColourPalette[ColourType.COLOUR_BLUE])
        glVertex2d(10 + self.widthSoFar, self.heightSoFar + 10 + MONITOR_BARHEIGHT)

        glColor4fv(ColourPalette[ColourType.COLOUR_GREEN])
        glVertex2d(10 + self.widthSoFar, self.heightSoFar + 10 + MONITOR_BARHEIGHT * (1 + animat.controls["left"]))

        glEnd()

        # Draw right motor
        glBegin(GL_LINE_STRIP)

        glColor4fv(ColourPalette[ColourType.COLOUR_BLUE])
        glVertex2d(20 + self.widthSoFar, self.heightSoFar + 10 + MONITOR_BARHEIGHT)
        glColor4fv(ColourPalette[ColourType.COLOUR_RED])
        glVertex2d(20 + self.widthSoFar, self.heightSoFar + 10 + MONITOR_BARHEIGHT * (1 + animat.controls["right"]))

        glEnd()

        # Draw sensors
        j = 0
        for sensor in animat.sensors:
            glBegin(GL_LINE_STRIP)

            glColor4fv(ColourPalette[ColourType.COLOUR_BLUE])
            glVertex2d(30 + (10 * j) + self.widthSoFar, self.heightSoFar + 10 + MONITOR_BARHEIGHT)
            glColor4fv(ColourPalette[ColourType.COLOUR_WHITE])
            glVertex2d(30 + (10 * j) + self.widthSoFar,
                       self.heightSoFar + 10 + MONITOR_BARHEIGHT * (1 + sensor.GetOutput()))

            glEnd()
            numBars += 1
            j += 1

        # Draw axes
        glLineWidth(1.0)
        glColor4fv(ColourPalette[ColourType.COLOUR_BLACK])
        glBegin(GL_LINES)

        # vertical right
        glVertex2d((numBars * 10) + self.widthSoFar + 5, self.heightSoFar + 10)
        glVertex2d((numBars * 10) + self.widthSoFar + 5, self.heightSoFar + 10 + (MONITOR_BARHEIGHT * 2))
        # vertical left
        glVertex2d(self.widthSoFar + 5, self.heightSoFar + 10)
        glVertex2d(self.widthSoFar + 5, self.heightSoFar + 10 + (MONITOR_BARHEIGHT * 2))
        # bottom
        glVertex2d((numBars * 10) + self.widthSoFar + 5, self.heightSoFar + 10)
        glVertex2d(self.widthSoFar + 5, self.heightSoFar + 10)
        # midpoint
        glVertex2d((numBars * 10) + self.widthSoFar + 5, self.heightSoFar + 10 + MONITOR_BARHEIGHT)
        glVertex2d(self.widthSoFar + 5, self.heightSoFar + 10 + MONITOR_BARHEIGHT)
        # top
        glVertex2d((numBars * 10) + self.widthSoFar + 5, self.heightSoFar + 10 + (MONITOR_BARHEIGHT * 2))
        glVertex2d(self.widthSoFar + 5, self.heightSoFar + 10 + (MONITOR_BARHEIGHT * 2))

        glEnd()

        # Set line width
        glLineWidth(1.0)

        # Draw bottom (colour coded)
        glColor4fv(animat.GetColour())
        glBegin(GL_LINES)
        glVertex2d((numBars * 10) + self.widthSoFar + 5, self.heightSoFar + 10)
        glVertex2d(self.widthSoFar + 5, self.heightSoFar + 10)
        glEnd()

        # Update widthSoFar
        self.widthSoFar += int(20 + len(animat.sensors) * 10)

        # Check if monitor exceeds width
        if self.widthSoFar + (10 * (2 + len(animat.sensors))) > animat.GetWorld().GetWidth():
            self.heightSoFar += (2 * MONITOR_BARHEIGHT) + 5
            self.widthSoFar = 0

        return

    def SetVisible(self, v):
        """
        Sets the visibility of the monitor.

        Args:
            v (bool): Boolean value indicating the visibility of the monitor.
        """
        self.visible = v

    def IsVisible(self):
        """
        Checks if the monitor is visible.

        Returns:
            bool: True if the monitor is visible, False otherwise.
        """
        return self.visible
