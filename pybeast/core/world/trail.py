# Built-in
from collections import deque
# Third-party
from OpenGL.GL import *
# Beast
from pybeast.core.world.drawable import Drawable

class Trail():
    def __init__(self,
        #N_points: int = 30,
        Visible: bool = True,
        trailWidth: float = 2.0,
        trailLength: int = 30,
        r: float = 1.0,
        g: float = 1.0,
        b: float = 1.0):

        self.colour = [r, g, b]
        self.trailWidth = trailWidth
        self.trailLength = trailLength
        self.visible = Visible
        self.points = []

    def Display(self):
        if not self.visible or not self.points:
            return

        glLineWidth(self.trailWidth)
        glEnable(GL_BLEND)
        glBegin(GL_LINE_STRIP)
        for i, point in enumerate(self.points):
            glColor4f(self.colour[0], self.colour[1], self.colour[2], i / len(self.points))
            glVertex2d(point.GetX(), point.GetY())

        glEnd()
        glDisable(GL_BLEND)
        glLineWidth(1.0)

    def Append(self, location):

        self.points.append(location)

    def Update(self):

        while len(self.points) > self.trailLength:
            self.points.pop(0)

    def Clear(self):
        self.points.clear()

    def SetColour(self, r, g, b):

        self.colour = [r, g, b]




