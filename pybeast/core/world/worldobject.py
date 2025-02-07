# Built-in
from __future__ import annotations
import sys
from typing import TYPE_CHECKING, List, Optional, Union
import numpy as np
# Local
from pybeast.core.world.drawable import Drawable, DRAWABLE_RADIUS
from pybeast.core.utils.vector2D import Vector2D

if TYPE_CHECKING:
    from pybeast.core.world.world import World

TWO_PI = 2 * np.pi

class WorldObject(Drawable):
    """The base class for everything that makes a difference in the world,
    including Animats, Sensors, and all types of scenery and interactive objects.

    WorldObject provides many overridable methods that ensure just about any kind of thing
    can be represented in the simulation environment. Of particular importance are `Init`,
    `Update`, `Interact`, and `OnCollision`, the main methods used in making a useful
    simulation object.

    WorldObject also handles some collision detection and provides methods for detecting
    if other objects are touching this one.
    """

    numWorldObject = 0

    def __init__(self,
            startLocation: Optional[Vector2D] = None,
            startOrientation: float = 0.0,
            radius: float = DRAWABLE_RADIUS,
            edges: Optional[List[Vector2D]] = None,
            solid: bool = False,
            ):

        super().__init__(startLocation, startOrientation, radius, edges = edges)

        self.solid = solid
        self.selectable = True
        self.absoluteEdges = []

        self.resetRandom = {}

        if startLocation is None:
            self.resetRandom['startLocation'] = True
        else:
            self.resetRandom['startLocation'] = False
        if startOrientation is None:
            self.resetRandom['startOrientation'] = True
        else:
            self.resetRandom['startOrientation'] = False

        self.isInit = False
        WorldObject.numWorldObject += 1

    def __del__(self):

        WorldObject.numWorldObject -= 1
        super().__del__()

    def Init(self):

        if self.startLocation is None:
            if self.myWorld is not None:
                self.startLocation = self.myWorld.RandomLocation()
            # This allows us to create and initialize objects and animats in tutorials without Simulation and World
            else:
                self.startLocation = Vector2D()

        if self.startOrientation is None:
            self.startOrientation = np.random.uniform(high=TWO_PI)

        self.SetLocation(self.startLocation)
        self.SetOrientation(self.startOrientation)

        if not self.IsCircular():
            self.CalcAbsoluteEdges()

        self.dead = False

        super().Init()

        self.isInit = True

    def Reset(self):

        if self.resetRandom['startLocation']:
            self.startLocation = self.myWorld.RandomLocation()
        if self.resetRandom['startOrientation']:
            self.startOrientation = np.random.uniform(high=TWO_PI)

        self.SetLocation(self.startLocation)
        self.SetOrientation(self.startOrientation)

        return

    def Interact(self, other: "WorldObject"):
        """
        Calls the one-way interact method of this and another WorldObject. See
        UniInteract for the use of one-way interactions.

        :param other: The WorldObject we're interacting with.
        """
        # TODO: Do we really need this?
        self.UniInteract(other)
        # TODO: This leads to infinite recursion
        #other.Interact(self)

    def UniInteract(self, other: "WorldObject"):
        # TODO: Do not know where this is defined in the c++
        pass

    def Update(self):
        """
        By default, worldobjects are not updated. Needs to be overwritten by child classes
        """
        #super().Update()


    def IsInside(self, vecTest: Vector2D) -> bool:
        """
        Returns true if the specified point is inside this object.

        :param vecTest: The point being tested.
        :return: True if vecTest is inside this object.
        """
        if self.IsCircular():
            return (vecTest - self.GetLocation()).GetLengthSquared() <= self.GetRadiusSquared()

        # Choose a point the right of vecTest which is outside the polygon
        vecOutside = vecTest + Vector2D(self.GetRadius() + 1.0, 0)

        inside = False

        # Ray casting algorithm: Iterate over all edges of the polygon
        for edge, nextEdge in zip(self.absoluteEdges[:-1], self.absoluteEdges[1:]):
            # For each edge we check wether the line from vecTest to vectOuside
            if (edge.y >= vecTest.y and nextEdge < vecTest.y) or (edge.y < vecTest.y and nextEdge.y >= vecTest.y):
                if self.CalcIntersect(edge, nextEdge, vecTest, vecOutside) is not None:
                    inside = not inside

        return inside

    def GetNearestPoint(self, vec: Vector2D):
        """
        Returns the nearest point on this object to the argument, and also returns
        the collision normal

        :param vec: The point we are comparing.
        :return: The normal between the nearest side to vec and vec.

        Returns:
            Vector2D: The nearest point on this object to vec.
        """
        if self.IsCircular():
            collisionNormal = (vec - self.GetLocation()).GetNormalized()
            collisionPoint = self.GetLocation() + collisionNormal * self.GetRadius()
            return collisionPoint, collisionNormal

        sideFound = False
        v1, v2 = None, None
        # TODO: Check if 'self.absoluteEdges' are vertexes or edges
        for vertex, nextVertex in zip(self.absoluteEdges[:-1], self.absoluteEdges[1:]):
            vec = self.CalcIntersect(vertex, nextVertex, vec, self.GetLocation())
            if vec:
                v1, v2 = vertex, nextVertex
                sideFound = True
                break

        # If no side was found, the point is inside so just return the same point
        if not sideFound:
            return vec

        collisionPoint = self.GetNearestPointOnLine(vec, v1, v2)
        collisionNormal = (v2 - v1).GetPerpendicular().GetNormalized()

        # Now we find the nearest point on the line l1-l2 to vec
        return collisionPoint, collisionNormal

    def GetNearestPointOnLine(self, vec: Vector2D, l1: Vector2D, l2: Vector2D) -> Vector2D:
        """
        Finds the nearest point on the line l1-l2 to vec and returns that point.

        :param vec: The point we're looking for the nearest point to.
        :param l1: The first vertex of the line.
        :param l2: The second vertex of the line.
        :return: The nearest point on the line to vec.
        """

        A = vec - l1
        B = l2 - l1
        theta = np.pi / 2 - (B.GetAngle() - A.GetAngle())
        distAlongSide = A.GetLength() * np.sin(theta)

        if distAlongSide > B.GetLength():
            return l2
        elif distAlongSide <= 0.0:
            return l1
        else:
            return l1 + B.GetNormalized() * distAlongSide

    def Intersects(self, l1: Vector2D, l2: Vector2D, intersection: Vector2D) -> bool:
        '''
        Returns true if the line defined by the two inputs intersects with this
        object at some point

        :param l1: The first point of the line to be tested.
        :param l2: The second point of the line to be tested.
        :return: True if the line intersects this object, false if not.
        '''
        # Object is circle
        if self.IsCircular():
            nearPoint = self.GetNearestPointOnLine(self.GetLocation(), l1, l2)
            distToLine = (self.GetLocation() - nearPoint).GetLength()

            if self.GetRadiusSquared() >= distToLine ** 2:
                l = np.sqrt(self.GetRadiusSquared() - distToLine** 2)
                l1_nearPoint = nearPoint - l1
                l1_nearPoint.SetLength(l1_nearPoint.GetLength() - l)
                vec = l1 + l1_nearPoint
                # TODO: This emulates C++ return by reference
                intersection.SetCartesian(vec.x, vec.y)
                return True
            return False
        # Object is Polygon
        else:
            vec = None
            found = False
            # Iterate over Polygon's edges
            for edge, nextEdge in zip(self.absoluteEdges[:-1], self.absoluteEdges[1:]):
                # Check if line through l1 and l2 intersects with edge
                vec = self.CalcIntersect(edge, nextEdge, l1, l2)
                if vec is not None:
                    if not found:
                        found = True
                        # TODO: This emulates C++ return by reference
                        intersection.SetCartesian(vec.x, vec.y)
                    elif (vec - l1).GetLengthSquared() < (intersection - l1).GetLengthSquared():
                        # TODO: This emulates C++ return by reference
                        intersection.SetCartesian(vec.x, vec.y)
            return found

    def CalcAbsoluteEdges(self):
        """
        Calculates a vector of absolute edge coordinates from the coordinates in
        the WorldObject's edges vector, which are relative to the object's
        location.
        """
        self.absoluteEdges.clear()
        m1 = np.cos(self.GetOrientation())
        m2 = np.sin(self.GetOrientation())

        for edge in self.edges:
            self.absoluteEdges.append(Vector2D(
                self.GetLocation().x + (m1 * edge.x - m2 * edge.y),
                self.GetLocation().y + (m1 * edge.y + m2 * edge.x)
            ))

    def CalcIntersect(self, a1: Vector2D, a2: Vector2D, b1: Vector2D, b2: Vector2D) -> Union[None, Vector2D]:
        """
        Takes four Vector2D coordinates describing two lines as input, and returns
        true if the line of the first two coordinates intersects that of the second
        two.

        :param a1: First vertex of the first line.
        :param a2: Second vertex of the first line.
        :param b1: First vertex of the second line.
        :param b2: Second vertex of the second line.
        :return: Intersect or None if there is none.
        """
        # Calculate both line equations from vectors
        dAGrad = (a2 - a1).GetGradient()
        dBGrad = (b2 - b1).GetGradient()
        dAYInt = a1.y - dAGrad * a1.x
        dBYInt = b1.y - dBGrad * b1.x

        # If they're parallel give up
        if dAGrad == dBGrad:
            return None

        # If a is vertical...
        if dAGrad == np.inf:
            r = Vector2D(a1.x, dBGrad * a1.x + dBYInt)
            if (((r.y <= a1.y and r.y >= a2.y) or (r.y <= a2.y and r.y >= a1.y))
                and ((r.y <= b1.y and r.y >= b2.y) or (r.y <= b2.y and r.y >= b1.y))
                and ((r.x <= b1.x and r.x >= b2.x) or (r.x <= b2.x and r.x >= b1.x))):

                return r

        # If b is vertical...
        if dBGrad == np.inf:
            r = Vector2D(b1.x, dAGrad * b1.x + dAYInt)
            if (((r.y <= a1.y and r.y >= a2.y) or (r.y <= a2.y and r.y >= a1.y))
                and ((r.y <= b1.y and r.y >= b2.y) or (r.y <= b2.y and r.y >= b1.y))
                and ((r.x <= a1.x and r.x >= a2.x) or (r.x <= a2.x and r.x >= a1.x))):

                return r

        # Find the intersections
        r = Vector2D(-(dAYInt - dBYInt) / (dAGrad - dBGrad), 0)
        r.y = dAGrad * r.x + dAYInt

        # Check if the intersection is inside the range of the two line segments
        if (((r.x <= a1.x and r.x >= a2.x) or (r.x <= a2.x and r.x >= a1.x))
            and ((r.x <= b1.x and r.x >= b2.x) or (r.x <= b2.x and r.x >= b1.x))):
            return r

        return None

    def OnClick(self):
        pass

    def OnSelect(self):
        pass

    def OnCollision(self, other):
        pass

    def IsSolid(self) -> bool:
        return self.solid


    def IsDead(self) -> bool:
        return self.dead


    def IsInitRandom(self) -> bool:
        return self.initRandom

    def IsSelectable(self) -> bool:
        return self.selectable


    def SetSolid(self, s: bool):
        self.solid = s


    def SetDead(self, d: bool):
        self.dead = d


    def SetResetRandom(self, r: bool):
        self.initRandom = r


    def SetMoveable(self, m: bool):
        self.moveable = m


    def SetSelectable(self, s: bool):
        self.selectable = s


    def _SetLogStream(self, o: sys.stdout):
        self.logStream = o


    @staticmethod
    def SetLogStream(o: sys.stdout):
        WorldObject.logStream = o

    @staticmethod
    def GetLogStream() -> sys.stdout:
        return WorldObject.logStream

WorldObject()