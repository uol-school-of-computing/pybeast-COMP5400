

# animatmonitor.py
"""
File: animatmonitor.py
Authors: Tom Carden, David Gordon
"""
from typing import List

# Thid-party
from OpenGL.GL import *
# Local
from pybeast.core.agents.animat import Animat
from pybeast.core.utils.colours import ColourPalette, ColourType



# Constants
MONITOR_BARHEIGHT = 25

class AnimatMonitor():
    # Placeholder for static visible attribute
    visible = False


    def __init__(self, animats: List[Animat]):

        self.animats = animats
        self.visible = True
        self.widthSoFar = 0
        self.heightSoFar = 0


    def Display(self):
        if self.visible:
            self.widthSoFar = self.heightSoFar = 0

            for a in self.animats: self.DrawBar(a)

    def Clear(self):

        self.animats.clear()

    def Append(self, animat: Animat):

        self.animats.append(animat)

    def DrawBar(self, animat):

        numBars = 2  # already counted motors

        # left motor (numBars++)
        glBegin(GL_LINE_STRIP)
        glColor4fv(ColourPalette[ColourType.COLOUR_BLUE])
        glVertex2d(10 + self.widthSoFar, self.heightSoFar + 10 + MONITOR_BARHEIGHT)
        glColor4fv(ColourPalette[ColourType.COLOUR_GREEN])
        glVertex2d(10 + self.widthSoFar, self.heightSoFar + 10 + MONITOR_BARHEIGHT * (1 + animat.controls["left"]))
        glEnd()

        # right motor (numBars++)
        glBegin(GL_LINE_STRIP)
        glColor4fv(ColourPalette[ColourType.COLOUR_BLUE])
        glVertex2d(20 + self.widthSoFar, self.heightSoFar + 10 + MONITOR_BARHEIGHT)
        glColor4fv(ColourPalette[ColourType.COLOUR_RED])
        glVertex2d(20 + self.widthSoFar, self.heightSoFar + 10 + MONITOR_BARHEIGHT * (1 + animat.controls["right"]))
        glEnd()

        # sensors
        j = 0
        for sensor in animat.sensors.values():
            glBegin(GL_LINE_STRIP)
            glColor4fv(ColourPalette[ColourType.COLOUR_BLUE])
            glVertex2d(30 + (10 * j) + self.widthSoFar, self.heightSoFar + 10 + MONITOR_BARHEIGHT)
            glColor4fv(ColourPalette[ColourType.COLOUR_WHITE])
            glVertex2d(30 + (10 * j) + self.widthSoFar,
                       self.heightSoFar + 10 + MONITOR_BARHEIGHT * (1 + sensor.GetOutput()))
            glEnd()
            numBars += 1
            j += 1

        # axes
        glBegin(GL_LINES)
        glColor4fv(ColourPalette[ColourType.COLOUR_BLACK])
        glVertex2d((numBars * 10) + self.widthSoFar + 5, self.heightSoFar + 10)
        glVertex2d((numBars * 10) + self.widthSoFar + 5, self.heightSoFar + 10 + (MONITOR_BARHEIGHT * 2))
        glVertex2d(self.widthSoFar + 5, self.heightSoFar + 10)
        glVertex2d(self.widthSoFar + 5, self.heightSoFar + 10 + (MONITOR_BARHEIGHT * 2))
        glVertex2d((numBars * 10) + self.widthSoFar + 5, self.heightSoFar + 10)
        glVertex2d(self.widthSoFar + 5, self.heightSoFar + 10)
        glVertex2d((numBars * 10) + self.widthSoFar + 5, self.heightSoFar + 10 + MONITOR_BARHEIGHT)
        glVertex2d(self.widthSoFar + 5, self.heightSoFar + 10 + MONITOR_BARHEIGHT)
        glVertex2d((numBars * 10) + self.widthSoFar + 5, self.heightSoFar + 10 + (MONITOR_BARHEIGHT * 2))
        glVertex2d(self.widthSoFar + 5, self.heightSoFar + 10 + (MONITOR_BARHEIGHT * 2))
        glEnd()

        glBegin(GL_LINES)
        glColor4fv(animat.GetColour())
        glVertex2d((numBars * 10) + self.widthSoFar + 5, self.heightSoFar + 10)
        glVertex2d(self.widthSoFar + 5, self.heightSoFar + 10)
        glEnd()

        self.widthSoFar += int(20 + len(animat.sensors) * 10)

        if self.widthSoFar + (10 * (2 + len(animat.sensors))) > self.animats[0].GetWorld().GetWidth():
            self.heightSoFar += (2 * MONITOR_BARHEIGHT) + 5
            self.widthSoFar = 0

    def SetVisible(self, v: bool):
        self.visible = v

    def IsVisible(self) -> bool:
        return self.visible

# TODO: Don't know what this is about
#AnimatMonitor.visible = False
