"""
Draws collisions in the World
Author: Tom Carden
"""
from collections import deque

# Third-party
from OpenGL.GL import *
from OpenGL.GLU import *
# Local
from pybeast.core.world.drawable import Drawable
from pybeast.core.utils.vector2D import Vector2D

MAX_COLLISIONS = 200

class Collision(Drawable):

    def __int__(self, location: Vector2D, visible: bool = False):

        super().__init__(location, visible = visible)

    def Display(self):
        """
        Overload Display from Drawable class
        """
        if not self.IsVisible():
            return

        Disk = gluNewQuadric()
        gluQuadricDrawStyle(Disk, GLU_FILL)
        glColor4f(0.9, 0.9, 0.1, 0.2)
        glEnable(GL_BLEND)

        glPushMatrix()
        glTranslated(self.location.GetX(), self.location.GetY(), 0)
        gluDisk(Disk, 0, 3, 10, 1)
        glPopMatrix()

        glDisable(GL_BLEND)
        gluDeleteQuadric(Disk)

class Collisions():
    def __init__(self, visible = False):

        self.collisions = []

    def __len__(self):
        return len(self.collisions)

    def Append(self, c: Collision):

        self.collisions.append(c)

    def Update(self):
        self.collisions = self.collisions[:MAX_COLLISIONS]

    def Clear(self):
        self.collisions.clear()

    def Display(self):

        for collision in self.collisions:
            collision.Display()






