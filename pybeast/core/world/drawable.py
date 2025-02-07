'''
Include this file if you wish to create scenery or other non-interactive
objects which appear in the world.
Everything that appears in the world is a Drawable, and all WorldObjects
and Animats are derived from it.
author Tom Carden
author David Gordon
'''
# Built-in
from __future__ import annotations
import io
import time
from typing import TYPE_CHECKING, List, Optional
import pickle
# Third-party
import numpy as np
from OpenGL.GL import *
# Pybeast
from pybeast.core.utils.vector2D import Vector2D

if TYPE_CHECKING:
    from pybeast.core.world.world import World

DRAWABLE_RADIUS = 50.0;	# The default radius for drawables.

class Drawable:
    def __init__(self,
        startLocation: Optional[Vector2D] = None,
        startOrientation: float = 0.0,
        radius: float = DRAWABLE_RADIUS,
        visible: bool = True,
        colour: List[float] = [0.5, 0.5, 0.5, 1.0],
        edges: Optional[List[Vector2D]] = None):

        self.startLocation = startLocation
        self.startOrientation = startOrientation

        self.radius = radius
        self.radius_squared = radius * radius
        self.visible = visible
        self.colour = colour
        self.edges = edges

        if edges is None:
            self.circular = True

        self.myWorld = None

        self.displaylist = 0

    def __del__(self):

        if self.displaylist != 0:
            glDeleteLists(self.displaylist, 1)

    def _repr(self, **kwargs):
        """
        Helper method to represent Drawable class and subclasses
        """
        class_name = self.__class__.__name__
        arg_str = ", ".join(f"{key}={value!r}" for key, value in kwargs.items())
        return f"{class_name}({arg_str})"

    def __repr__(self) -> str:

        return self._repr(location=self.location, orientation=self.orientation, radius=self.radius,
            colour = self.colour, edges = self.edges)

    #-------------------------------------------------------------------------------------------------------------------
    # Drawable interface methods
    #-------------------------------------------------------------------------------------------------------------------

    def Init(self) -> None:
        """
        Initialises the GL display list and figures out the effective radius of
        non-circular objects.
        Drawable.Draw
        """
        # Allocate a free Display list index, deleting any existing display list first
        if self.displaylist != 0:
            glDeleteLists(self.displaylist, 1)

        self.displaylist = glGenLists(1)

        # Define the Display list:
        glNewList(self.displaylist, GL_COMPILE)
        self.Draw()
        glEndList()

        if not self.circular:
            for e in self.edges:
                if e.GetLengthSquared() > self.radiusSquared:
                    self.SetRadius(e.GetLength())

    def Display(self) -> None:

        if not self.visible:
            return

        glPushMatrix()
        glTranslated(self.location.x, self.location.y, 0.0)
        glRotated(np.degrees(self.orientation), 0.0, 0.0, 1.0)
        self.Render()
        glPopMatrix()

    def Render(self) -> None:
        #print(f'displaylist from Drawable.Render: {self.displaylist}')

        if self.displaylist == 0:
            import traceback
            traceback.print_exc()

        glCallList(self.displaylist)

    def Draw(self) -> None:

        sides = 15.0 if self.circular else len(self.edges)
        glBegin(GL_POLYGON)
        if self.circular:
            for f in range(int(sides)):
                pos = f / sides
                glColor4f(
                    self.colour[0] * (1 - pos ** 2),
                    self.colour[1] * (1 - pos ** 2),
                    self.colour[2] * (1 - pos ** 2),
                    self.colour[3]
                )
                glVertex2d(self.radius * np.sin(pos * 2 * np.pi), self.radius * np.cos(pos * 2 * np.pi))
        else:
            for f in range(len(self.edges)):
                pos = f / sides
                glColor4f(
                    self.colour[0] * (1 - pos ** 2),
                    self.colour[1] * (1 - pos ** 2),
                    self.colour[2] * (1 - pos ** 2),
                    self.colour[3]
                )
                glVertex2d(self.edges[f].x, self.edges[f].y)
                f += 1
        glEnd()

    #------------------------------------------------------------------------------------------------------------------
    # Accessors
    #------------------------------------------------------------------------------------------------------------------

    def GetDisplayList(self):
        return self.displaylist

    def GetColour(self) -> List[float]:
        return self.colour

    def GetLocation(self) -> Vector2D:
        return self.location

    def GetColourAtIndex(self, i: int) -> float:
        return self.colour[i]

    def GetOrientation(self) -> float:
        return self.orientation

    def GetDiameter(self) -> float:
        return self.radius * 2

    def GetRadius(self) -> float:
        return self.radius

    def GetRadiusSquared(self) -> float:
        return self.radius_squared

    def IsCircular(self) -> bool:
        return self.circular

    def IsPolygon(self) -> bool:
        return not self.circular

    def IsVisible(self) -> bool:
        return self.visible

    def GetWorld(self):
        return self.myWorld

    #------------------------------------------------------------------------------------------------------------------
    # Mutators
    #------------------------------------------------------------------------------------------------------------------

    def SetColour(self, r: float, g: float, b: float, a: float = 1.0):
        self.colour = [r, g, b, a]

    def SetLocation(self, pv: Vector2D):
        self.location = pv

    def SetLocationFromCoordinates(self, x: float, y: float):
        self.location = np.array([x, y])

    def SetLocationX(self, x: float):
        self.location.x = x

    def SetLocationY(self, y: float):
        self.location.y = y

    def OffsetLocation(self, pv: Vector2D):
        self.location += pv

    def OffsetLocationByCoordinates(self, x: float, y: float):
        self.location += Vector2D(x, y)

    def SetOrientation(self, o: float):
        self.orientation = o
        self.orientation %= 2*np.pi

    def OffsetOrientation(self, o: float):
        self.orientation += o
        if self.orientation < 0:
            self.orientation += 2*np.pi
        self.orientation %= 2*np.pi

    def SetRadius(self, r: float):
        self.radius = r
        self.radius_squared = r**2

    def SetWorld(self, world: Optional[World] = None):
        self.myWorld = world

    def SetVisible(self, v: bool):
        self.visible = v

    def SetColourFromArray(self, col: List[float]):
        self.colour = col

    #------------------------------------------------------------------------------------------------------------------
    # Serialise
    #------------------------------------------------------------------------------------------------------------------

    def Serialise(self, filename=None):

        # if no filename is given
        if filename is None:
            outputStream = io.BytesIO()
            pickle.dump(self, outputStream)
        else:
            with open(filename, 'wb') as jf:
                pickle.dump(self, filename)


    @staticmethod
    def Unserialise(filename) -> "Drawable":

        # if no filename is given
        if filename is None:
            inputStream = io.BytesIO().getvalue()
            instance = pickle.load(inputStream)
        else:
            with open(filename, 'rb') as file:
                instance = pickle.load(file)

        return instance