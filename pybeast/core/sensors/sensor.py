"""
File: sensor.py
Author: David Gordon
"""
# Built-in
from typing import TypeVar
from operator import truediv

# Third-party
import numpy as np

#Beast
from pybeast.core.sensors.sensorbase import *
from pybeast.core.sensors.sensorfunctors import *
from pybeast.core.world.worldobject import WorldObject

# Define a TypeVar representing a subclass of WorldObject
T = TypeVar('T', bound=WorldObject)

def ProximitySensor(detectedType: T, scope: float, range: float, orientation: float, simple = False,
        outputMinmum = 1.0, outputMaximum = 0.0) -> Sensor:
    """
    Creates a segment-shaped sensor with the specified scope, range, and orientation
    which detects the distance of objects of the specified templated type.
    """
    if not simple:
        s = BeamSensor(scope, range, relOrientation = orientation)
        s.SetEvaluationFunction(EvalBeam(s, scope, range))
    else:
        s = BeamSensor(scope, range, relOrientation=orientation)
        s.SetEvaluationFunction(EvalNearestInScope(s, scope, range))

    s.SetMatchingFunction(MatchKindOf(detectedType))

    # Scale function flips input and out range, i.e. largest/smallest input yields smallest/largest output
    s.SetScalingFunction(ScaleLinear(0.0, range, outputMinmum, outputMaximum))

    return s

#
def NearestAngleSensor(detectedType: T, range: float = 1000.0, reverseScale = False) -> Sensor:
    """
    Creates a sensor to detect the nearest angle.
    """
    s = Sensor()
    s.SetMatchingFunction(MatchKindOf(detectedType))
    s.SetEvaluationFunction(EvalNearestAngle(s, range))
    if not reverseScale:
        s.SetScalingFunction(ScaleLinear(-np.pi, np.pi, -1.0, 1.0))
    else:
        s.SetScalingFunction(ScaleLinear(-np.pi, np.pi, 1.0, -1.0))

    return s

def NearestXSensor(detectedType: T, range: float = 1000.0) -> Sensor:
    """
    Creates a sensor to detect the nearest x-coordinate.
    """
    s = Sensor(Vector2D(), 0.0)
    s.SetMatchingFunction(MatchKindOf(detectedType))
    s.SetEvaluationFunction(EvalNearestXDist(s, range))
    s.ScalingFunction = ScaleLinear(-500.0, 500.0, -1.0, 1.0)

def NearestYSensor(detectedType: T, range: float = 1000.0) -> Sensor:
    """
    Creates a sensor to detect the nearest y-coordinate.
    """
    s = Sensor(Vector2D(), 0.0)
    s.SetMatchingFunction(MatchKindOf(detectedType))
    s.SetEvaluationFunction(EvalNearestYDist(s, range))
    s.ScalingFunction = ScaleLinear(-500.0, 500.0, -1.0, 1.0)
    return s

def DensitySensor(detectedType: T, scope: float, range: float, orientation: float) -> Sensor:
    """
    Creates a sensor to measure density within a specified scope, range, and orientation.
    """
    s = BeamSensor(scope, range, Vector2D(), orientation)
    s.SetDrawFixed(True)
    s.SetMatchingFunction(MatchKindOf(detectedType))
    s.SetEvaluationFunction(EvalCount(1))
    s.SetScalingFunction(ScaleCompose(ScaleAdapter(lambda f: truediv(1.0, f)), ScaleLinear(0.0, 1.0, 1.0, 0.0)))
    return s


def CollisionSensor(detectedType: T, threshold: float = 1.0) -> Sensor:
    s = TouchSensor()
    s.SetMatchingFunction(MatchKindOf(detectedType))
    s.SetEvaluationFunction(EvalCount())
    s.SetScalingFunction(ScaleThreshold(1.0))
    return s