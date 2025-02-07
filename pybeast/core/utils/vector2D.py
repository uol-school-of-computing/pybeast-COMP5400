# Built-in
import sys
# Third-party
import numpy as np
# Constants
TWO_PI = 2*np.pi

class Vector2D:
    def __init__(self, X=0.0, Y=0.0, l=None, a=None, v=None):

        if v is not None:
            assert a is not None
            assert l is not None
            self.x = v.x + l*np.cos(a)
            self.y = v.y + l*np.sin(a)
        elif l is not None:
            assert a is not None
            self.x = X + l*np.cos(a)
            self.y = Y + l*np.sin(a)
        else:
            self.x = X
            self.y = Y

    # Overloaded operators...
    def __add__(self, other):
        return Vector2D(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return Vector2D(self.x - other.x, self.y - other.y)

    def __mul__(self, scalar):
        return Vector2D(self.x * scalar, self.y * scalar)

    def __rmul__(self, scalar):
        return self.__mul__(scalar)

    def __neg__(self):
        return Vector2D(-self.x, -self.y)

    def __iadd__(self, other):
        self.x += other.x
        self.y += other.y
        return self

    def __isub__(self, other):
        self.x -= other.x
        self.y -= other.y
        return self

    def __imul__(self, scalar):
        self.x *= scalar
        self.y *= scalar
        return self

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __ne__(self, other):
        return self.x != other.x or self.y != other.y

    # Mutators...
    def SetX(self, X):
        self.x = X

    def SetY(self, Y):
        self.y = Y

    def SetPolarCoordinates(self, l, a):
        self.x = l * np.cos(a)
        self.y = l * np.sin(a)

    def SetCartesian(self, X, Y):
        self.x = X
        self.y = Y

    def SetLength(self, l):
        self.Normalize()
        self *= l

    def IncLength(self, l):
        self.Normalize()
        self *= l
        return True

    def DecLength(self, l):
        self.Normalize()
        self *= l
        return True

    def SetAngle(self, a):
        self.x = np.cos(a)
        self.y = np.sin(a)

    def Normalize(self):
        length = self.GetLength()
        if length != 0:
            self *= 1.0 / length

    def Rotate(self, a):
        m1 = np.cos(a)
        m2 = np.sin(a)
        self.x, self.y = m1 * self.x - m2 * self.y, m1 * self.y + m2 * self.x

    def Rotation(self, a):
        m1 = np.cos(a)
        m2 = np.sin(a)
        return Vector2D(m1 * self.x - m2 * self.y, m1 * self.y + m2 * self.x)

    # Accessors...
    def GetLength(self):
        return np.sqrt(self.GetLengthSquared())

    def GetLengthSquared(self):
        return self.x * self.x + self.y * self.y

    def GetAngle(self):
        angle = np.arctan2(self.y, self.x)
        if angle < 0:
            angle += 2*np.pi
        return angle

    def GetGradient(self):
        return self.y / self.x if self.x != 0 else np.max

    def GetReciprocal(self):
        return Vector2D(-self.x, -self.y)

    def GetNormalized(self):
        length = self.GetLength()
        if length != 0:
            return Vector2D(self.x / length, self.y / length)
        else:
            return Vector2D(0.0, 1.0)

    def GetPerpendicular(self):
        return Vector2D(-self.y, self.x)

    def Dot(self, other):
        return self.x * other.x + self.y * other.y

    def Serialise(self, out):
        out.write(f"Vector2D {self.x} {self.y}\n")

    def GetX(self):
        return self.x

    def GetY(self):
        return self.y

    def Unserialise(self, inp):
        name = inp.readline().strip()
        if name != "Vector2D":
            raise ValueError(f"Expected 'Vector2D' but got '{name}'")
        self.x, self.y = map(float, inp.readline().split())


# Non-member functions...
def deg2rad(angle):
    return angle / 360.0 * TWO_PI


def rad2deg(angle):
    return (angle / TWO_PI) * 360.0


def polar_vector(l, a):
    return Vector2D(0.0, 0.0, l, a)


# Output operator for Vector2D
def vector2d_output(out, v):
    v.Serialise(out)
    return out


# Input operator for Vector2D
def vector2d_input(inp):
    v = Vector2D()
    v.Unserialise(inp)
    return v
