import numpy as np

class Vector3D:
    def __init__(self, x=0.0, y=0.0, z=0.0):
        self.x = x
        self.y = y
        self.z = z

    def __add__(self, other):
        return Vector3D(self.x + other.x, self.y + other.y, self.z + other.z)

    def __sub__(self, other):
        return Vector3D(self.x - other.x, self.y - other.y, self.z - other.z)

    def __mul__(self, scalar):
        return Vector3D(self.x * scalar, self.y * scalar, self.z * scalar)

    def __rmul__(self, scalar):
        return self.__mul__(scalar)

    def __neg__(self):
        return Vector3D(-self.x, -self.y, -self.z)

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y and self.z == other.z

    def __ne__(self, other):
        return not self.__eq__(other)


    def __str__(self):
        return f"Vector3D({self.x}, {self.y}, {self.z})"

    def __repr__(self):
        return f"Vector3D({self.x}, {self.y}, {self.z})"

    def Length(self):
        return np.sqrt(self.x ** 2 + self.y ** 2 + self.z ** 2)

    def LengthSquared(self):
        return self.x ** 2 + self.y ** 2 + self.z ** 2

    def Normalize(self):
        length = self.Length()
        if length != 0:
            self.x /= length
            self.y /= length
            self.z /= length

    def Dot(self, other):
        return self.x * other.x + self.y * other.y + self.z * other.z

    def Cross(self, other):
        return Vector3D(self.y * other.z - self.z * other.y,
                        self.z * other.x - self.x * other.z,
                        self.x * other.y - self.y * other.x)

    def Rotate(self, angle, axis):
        c = np.cos(angle)
        s = np.sin(angle)
        axis.Normalize()
        x, y, z = axis.x, axis.y, axis.z
        matrix = [x*2*(1-c)+c, x*y*(1-c)-z*s, x*z*(1-c)+y*s, 0.0,
                  y*x*(1-c)+z*s, y*2*(1-c)+c, y*z*(1-c)-x*s, 0.0,
                  x*z*(1-c)-y*s, y*z*(1-c)+x*s, z*2*(1-c)+c, 0.0,
                  0.0, 0.0, 0.0, 1.0]
        temp = [0.0, 0.0, 0.0, 0.0]

        for i in range(4):
            pos = 4 * i
            temp[i] = self.x * matrix[pos] + self.y * matrix[pos + 1] + self.z * matrix[pos + 2] + 1.0 * matrix[pos + 3]
        self.x, self.y, self.z = temp[0], temp[1], temp[2]


# def V3MultMatrix(v, matrix):
#     temp = [0.0, 0.0, 0.0, 1.0]
#     for i in range(4):
#         pos = 4 * i
#         temp[i] = v.x * matrix[pos] + v.y * matrix[pos + 1] + v.z * matrix[pos + 2] + 1.0 * matrix[pos + 3]
#     return Vector3D(temp[0], temp[1], temp[2])
#
#
# def Rotate(vec, angle, axis):
#     c = np.cos(angle)
#     s = np.sin(angle)
#     axis.normalize()
#     x, y, z = axis.x, axis.y, axis.z
#     matrix = [x*2*(1-c)+c, x*y*(1-c)-z*s, x*z*(1-c)+y*s, 0.0,
#               y*x*(1-c)+z*s, y*2*(1-c)+c, y*z*(1-c)-x*s, 0.0,
#               x*z*(1-c)-y*s, y*z*(1-c)+x*s, z*2*(1-c)+c, 0.0,
#               0.0, 0.0, 0.0, 1.0]
#     return V3MultMatrix(vec, matrix)


