"""
Implements a two-dimensional density distribution.
@author: David Gordon
"""

import  numpy as np

from tynp.ping import Callable

from pybeast.core.world.worldobject import WorldObject
from pybeast.core.sensors.sensor import Sensor

class Distribution(WorldObject):
    def __init__(self,
        c: int,
        r: int,
        b: int = 1):

        super().__init__()
        self.kernel = Kernel(1, 1)
        self.rows = r
        self.cols = c
        self.tRows = r + 2 * b
        self.tCols = c + 2 * b
        self.border = b
        self.maxConc = 0.0
        self.diffusionSpeed = 0
        self.nextDiffusion = 0
        self.width = 0.0
        self.height = 0.0
        self.colSize = 0.0
        self.rowSize = 0.0
        self.distribution = [0.0] * (self.tCols * self.tRows)
        self.swapbuffer = [0.0] * (self.tCols * self.tRows)

    def init(self):
        pass

    def update(self):
        if self.diffusionSpeed > 0 and self.nextDiffusion <= 0:
            self.nextDiffusion = self.diffusionSpeed
            self.kernel.filter(self)

    def render(self):
        pass

    def set_diffusion_speed(self, s: int):
        self.diffusionSpeed = s
        self.nextDiffusion = s

    def set_decay_rate(self, r: float):
        self.kernel.set_divisor(r)

    def set_max_conc(self, f: float):
        self.maxConc = f

    def get_kernel(self):
        return self.kernel

    def value_at(self, x: int, y: int) -> float:
        return self.distribution[y * self.tCols + x]

    def get_density(self, x: int, y: int) -> float:
        x += self.border
        y += self.border
        return self.value_at(x, y)

    def get_density_vector(self, v: np.ndarray) -> float:
        pass

    def get_gradient(self, v: np.ndarray, o: float) -> float:
        pass

    def get_gradient_vector(self, x: int, y: int) -> np.ndarray:
        pass

    def get_gradient_vector(self, v: np.ndarray) -> np.ndarray:
        pass

    def set_density(self, x: int, y: int, d: float):
        self.value_at(x + self.border, y + self.border) = d

    def set_density_vector(self, v: np.ndarray, d: float):
        pass

    def add_density(self, x: int, y: int, d: float):
        self.value_at(x + self.border, y + self.border) += d

    def add_density_vector(self, v: np.ndarray, d: float):
        pass

    def plot(self, val: float):
        pass


class Kernel:
    def __init__(self, w: int, h: int):
        self.width = w // 2 * 2 + 1
        self.height = h // 2 * 2 + 1
        self.kernel = [0.0] * (w * h)

    def set_distribution(self, distribution: Distribution):
        pass

    def set(self, x: int, y: int, v: float):
        self.kernel[y * self.width + x] = v

    def set_divisor(self, d: float):
        pass

    def normalize(self):
        pass

    def get(self, x: int, y: int) -> float:
        return self.kernel[y * self.width + x]

    def filter(self, distribution: Distribution):
        pass

    def plot(self, func: Callable[[int, int], float]):
        d = self.kernel
        x = 0
        for y in range(self.width):
            for x in range(self.height):
                d = func(x, y)

    def plot(self, func: Callable[[int, int], float]):
        pass

    def filter(self, distribution: Distribution):
        pass


class EvalDensity(SensorEvalFunction):
    def __init__(self, owner: WorldObject):
        super().__init__()
        self.density = 0.0
        self.owner = owner

    def __call__(self, o: WorldObject, v: np.ndarray):
        pass

    def get_output(self) -> float:
        return self.density


class ScaleGradient(SensorScaleFunction):
    def __call__(self, n: float) -> float:
        return 2.0 * atan(n) / np.pi


class EvalGradient(SensorEvalFunction):
    def __init__(self, owner: WorldObject):
        super().__init__()
        self.gradient = 0.0
        self.owner = owner

    def __call__(self, o: WorldObject, v: np.ndarray):
        pass

    def get_output(self) -> float:
        return self.gradient


def gradient_sensor() -> Sensor:
    pass


def distribution_sensor() -> Sensor:
    pass
