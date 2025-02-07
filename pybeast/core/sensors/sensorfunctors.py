# Built-in
from abc import ABC, abstractmethod
import random
from typing import Callable

import numpy as np
# Third-party
from numpy import pi

# Beast
from pybeast.core.sensors.sensorbase import SensorMatchFunction, SensorEvalFunction, SensorScaleFunction
from pybeast.core.world.worldobject import WorldObject
from pybeast.core.utils.vector2D import Vector2D

class SensorMatchFunction(ABC):
    """Abstract base class for sensor match functions."""

    def __init__(self, objectType):

        self.objectType = objectType

    @abstractmethod
    def __call__(self, obj: WorldObject) -> bool:
        '''Method to be implemented by subclasses.

           :param obj: The object to check.
           :return: True if the object matches the criteria, False otherwise.
        '''
        pass

class MatchKindOf(SensorMatchFunction):
    """Base class for sensor match functions."""

    def __init__(self, objectType):

        super().__init__(objectType)

    def __call__(self, obj):
        """Check if the object is of the specified type or its subclass.

          Args:
              obj: The object to check.

          Returns:
              bool: True if the object is of the specified type or its subclass, False otherwise.
          """
        return isinstance(obj, self.objectType) or issubclass(type(obj), self.objectType)


class MatchExact(SensorMatchFunction):
    """
    Identifies exact object types, so if defined with Cheese, will return true
    only for Cheese, and false for Cheddar and Gruyère.
    """
    def __init__(self, objectType = WorldObject):

        self.objectType = objectType

    def __call__(self, obj: WorldObject) -> bool:
        """
        Checks if the given object's type matches the specified object type.

        Args:
            obj (WorldObject): The object to check.

        Returns:
            bool: True if the object's type matches the specified object type, False otherwise.
        """
        return isinstance(obj, self.objectType)

class MatchSpecific(SensorMatchFunction):
    """
    Identifies one particular object and returns true only for that object.
    """
    def __init__(self, obj: WorldObject):
        """
        Initializes the MatchSpecific object with the target object.

        Args:
            obj (WorldObject): The target object.
        """
        self.target = obj

    def __call__(self, obj: WorldObject) -> bool:
        """
        Checks if the given object is the same as the target object.

        Args:
            obj (WorldObject): The object to check.

        Returns:
            bool: True if the object is the same as the target object, False otherwise.
        """
        return obj is self.target

class MatchComposeOr():
    """
    Chains any number of matching functions together such that should any of
    them be true for the object being matched, MatchComposeOr will return true.
    """
    def __init__(self,
        first: SensorMatchFunction = None,
        second: SensorMatchFunction = None):
        """
        Initializes a MatchComposeOr object with optional first and second matching functions.

        Args:
            first (SensorMatchFunction, optional): The first matching function. Defaults to None.
            second (SensorMatchFunction, optional): The second matching function. Defaults to None.
        """
        self.matchFunctions = [first, second]

    def __del__(self):
        """
        Deletes the contained matching functions.
        """
        for func in self:
            del func

    def __call__(self, obj: WorldObject) -> bool:
        """
        Calls each matching function and returns True if any of them return True.

        Args:
            obj (WorldObject): The object to match.

        Returns:
            bool: True if any of the matching functions return True, False otherwise.
        """
        for func in self.matchFunctions:
            if func(obj):
                return True

        return False

class MatchComposeAnd():
    """
    Chains any number of matching functions together such that only if all of
    them are true for the object being matched, MatchComposeAnd will return
    true.
    """
    def __init__(self,
        first: SensorMatchFunction = None,
        second: SensorMatchFunction = None):
        """
        Initializes a MatchComposeAnd object with optional first and second matching functions.

        Args:
            first (SensorMatchFunction, optional): The first matching function. Defaults to None.
            second (SensorMatchFunction, optional): The second matching function. Defaults to None.
        """
        self.matchFunctions = [first, second]

    def __del__(self):
        """
        Deletes the contained matching functions.
        """
        for func in self:
            del func

    def __call__(self, obj: WorldObject) -> bool:
        """
        Calls each matching function and returns True if all of them return True.

        Args:
            obj (WorldObject): The object to match.

        Returns:
            bool: True if all of the matching functions return True, False otherwise.
        """
        for func in self.matchFunctions:
            if not func(obj):
                return False
        return True


class MatchAdapter(SensorMatchFunction):
    """
    Allows any unary predicate to be adapted for use as a matching function.
    """
    def __init__(self,
        functor: Callable[[WorldObject], None]):
        """
        Initializes a MatchAdapter object with the specified functor.

        :param functor: The functor to be adapted.
        """
        self.functor = functor

    def __call__(self, obj: WorldObject) -> bool:
        """
        Calls the functor with the input object and returns the result.

        :param obj: The input object to be matched.
        """

        return self.functor(obj)

def MatchAdapt(f: callable) -> MatchAdapter:
    """
    A helper function for creating MatchAdapter functors.

    Args:
        f (callable): The functor to be adapted.

    Returns:
        MatchAdapter: The adapted functor.
    """
    return MatchAdapter(f)

class EvalNearest(SensorEvalFunction):
    """
    Keeps a tally of the nearest point passed in and returns it with GetOutput.
    Also keeps a pointer to the nearest candidate and a copy of the nearest
    point on that candidate, this data can be accessed by an adapter such as
    EvalXDist and EvalAngle.
    """
    def __init__(self, owner: WorldObject, range: float):
        """
        Initializes the EvalNearest object with the owner and range.

        Args:
            owner (WorldObject): The owner of the evaluation.
            range (float): The range within which to evaluate.
        """
        self.owner = owner
        self.range = range
        self.nearestSoFar = range
        self.bestCandidate = None
        self.bestCandidateVec = None
        self.distance = 0.0
        self.threshold = 1.0

    def Reset(self):
        """
        Resets the evaluation to its initial state.
        """
        self.bestCandidate = None
        self.nearestSoFar = self.range

    def __call__(self, obj: WorldObject, loc: Vector2D):
        """
        Performs the evaluation.

        Args:
            obj (WorldObject): The detected object.
            loc (Vector2D): The location of the object.
        """
        self.distance = (self.owner.GetLocation() - loc).GetLength()

        if self.distance < self.nearestSoFar:
            self.nearestSoFar = self.distance
            self.bestCandidate = obj
            self.bestCandidateVec = loc

    def GetOutput(self) -> float:
        """
        Returns the output of the evaluation.

        Returns:
            float: The output value.
        """

        #nearestSoFar = min(self.nearestSoFar, self.threshold)

        return self.nearestSoFar

class EvalNearestInScope(EvalNearest):
    """
    Keeps a tally of the nearest point in scope in and returns it with GetOutput.
    """

    def __init__(self, owner: WorldObject, scope: float, range: float):

        self.scope = scope
        super().__init__(owner, range)

    def __call__(self, other, vec):

        if self.scope == 2*pi:
            super().__call__(other, vec)
        elif self.owner.InScope(vec):
            super().__call__(other, vec)


class EvalBeam(EvalNearest):
    """
    Keeps a tally of the nearest point in beam in and returns it with GetOutput.
    """
    def __init__(self, owner, scope, range, wrap = False):

        super().__init__(owner, range)

        self.scope = scope


    def Eval(self, other):
        """
        Uses a number of collision detection functions to locate the nearest point
        of the nearest object in scope. Automatic optimization in the case of 360
        degree scope.
        """
        # First find the nearest point on other to the sensor's origin
        s = self.owner

        vec, _ = other.GetNearestPoint(s.GetLocation())


        # If the nearest point on other is within scope
        if s.InScope(vec):
            super().__call__(other, vec)
        else:
            # Find the two edges of the beam and check intersections with shape. The "scope > 0.0" part ensures we
            # only do one test if the sensor is a laser.

            o = s.GetOrientation() - 0.5 * self.scope
            if o < 0:
                o += 2*np.pi

            sensorBeamEdge = Vector2D(l=self.range, a=o, v=s.GetLocation())

            if other.Intersects(self.owner.GetLocation(), sensorBeamEdge, vec):
                super().__call__(other, vec)

            # Even if the first test was successful, we test again in case both edges of the beam are intersecting the shape.
            sensorBeamEdge = Vector2D(l=self.range, a=s.GetOrientation() + self.scope * 0.5, v=s.GetLocation())

            if self.scope > 0.0 and other.Intersects(s.GetLocation(), sensorBeamEdge, vec):
                super().__call__(other, vec)

    def __call__(self, other, location):
        # this nees to become the beam sensors interact function

        """
        A wrapper for _Interact (the real interaction method) for handling wrapping.
        """
        self.Eval(other)

        # If wrapping is True, sensor detects objects through periodic boundaries
        if not self.owner.wrap:
            return

        if self.wrapping['Left']:
            temp = self.owner.GetLocation().x
            self.owner.SetLocationX(temp + self.myOwner.GetWorld().GetWidth())
            self.Eval(other)
            self.owner.SetLocationX(temp)

        if self.wrapping['Bottom']:
            temp = self.owner.GetLocation().y
            self.owner.SetLocationY(temp + self.myOwner.GetWorld().GetHeight())
            self.Eval(other)
            self.owner.SetLocationY(temp)

        if self.wrapping['Right']:
            temp = self.owner.GetLocation().x
            self.SetLocationX(temp - self.owner.GetWorld().GetWidth())
            self.Eval(other)
            self.owner.SetLocationX(temp)

        if self.wrapping['Top']:
            temp = self.owner.GetLocation().y
            self.owner.SetLocationY(temp - self.myOwner.GetWorld().GetHeight())
            self.Eval(other)
            self.owner.SetLocationY(temp)

class EvalNearestXDist(EvalNearest):
    def __init__(self, owner: WorldObject, range: float):
        """
        Initializes the EvalNearestXDist object.

        Args:
            owner (WorldObject): The owner of the evaluation.
            range (float): The range within which to evaluate.
        """
        super().__init__(owner, range)
    """
    Returns the vertical distance to the nearest target.
    Most effective when coupled with EvalNearestYDist.
    """

    def GetOutput(self) -> float:
        """
        Returns the vertical distance to the nearest target.

        Returns:
            float: The vertical distance.
        """
        return self.bestCandidateVec.x - self.owner.GetLocation().x

class EvalNearestYDist(EvalNearest):
    """
    Returns the horizontal distance to the nearest target.
    Most effective when coupled with EvalNearestXDist.
    """
    def __init__(self, owner: WorldObject, range: float):
        """
        Initializes the EvalNearestYDist object.

        Args:
            owner (WorldObject): The owner of the evaluation.
            range (float): The range within which to evaluate.
        """
        super().__init__(owner, range)

    def GetOutput(self) -> float:
        """
        Returns the horizontal distance to the nearest target.

        Returns:
            float: The horizontal distance.
        """
        return self.bestCandidateVec.y - self.owner.GetLocation().y

class EvalNearestAbsX(EvalNearest):
    """
    Returns the absolute x position of the nearest target.
    Most effective when coupled with EvalNearestAbsY.
    """
    def __init__(self, owner: WorldObject, range: float):
        """
        Initializes the EvalNearestAbsX object.

        Args:
            owner (WorldObject): The owner of the evaluation.
            range (float): The range within which to evaluate.
        """
        super().__init__(owner, range)

    def GetOutput(self) -> float:
        """
        Returns the absolute x position of the nearest target.

        Returns:
            float: The absolute x position.
        """
        return self.bestCandidateVec.x

class EvalNearestAbsY(EvalNearest):
    """
    Returns the absolute y position of the nearest target.
    Most effective when coupled with EvalNearestAbsX.
    """
    def __init__(self, owner: WorldObject, range: float):
        """
        Initializes the EvalNearestAbsY object.

        Args:
            owner (WorldObject): The owner of the evaluation.
            range (float): The range within which to evaluate.
        """
        super().__init__(owner, range)

    def GetOutput(self) -> float:
        """
        Returns the absolute y position of the nearest target.

        Returns:
            float: The absolute y position.
        """
        return self.bestCandidateVec.y


class EvalNearestAngle(EvalNearest):
    """
    Returns the normalized angle to the nearest target.
    """
    def __init__(self, owner: WorldObject, range: float):
        """
        Initializes the EvalNearestAngle object.

        Args:
            owner (WorldObject): The owner of the evaluation.
            range (float): The range within which to evaluate.
        """
        super().__init__(owner, range)

    def GetOutput(self) -> float:
        """
        Returns angle to the nearest target.

        Returns:
            float: The normalized angle.
        """
        # This can happen if no object has been detected within the sensor range
        if self.bestCandidate is None:
            angle = 0.0
        # Calculate relative angle to nearest detected object
        else:
            angle = (self.bestCandidateVec - self.owner.GetLocation()).GetAngle() - self.owner.GetOrientation()
            if angle > np.pi: angle -= 2*np.pi
        return angle

class EvalCount(SensorEvalFunction):
    """
    Keeps a total of every time it's called per round. Starting count may
    be defined but defaults to 0.
    """
    def __init__(self, start=0):
        """
        Initializes EvalCount object.

        Args:
            start (int, optional): Starting count. Defaults to 0.
        """
        self.startingCount = start
        self.numberSoFar = 0

    def Reset(self):
        """Resets the count."""
        self.numberSoFar = 0

    def __call__(self, obj: WorldObject, loc: Vector2D):
        """Increments the count."""
        self.numberSoFar += 1

    def GetOutput(self) -> float:
        """
        Gets the total count.

        Returns:
            float: Total count.
        """
        return float(self.numberSoFar + self.startingCount)

class EvalProximity():
    """
    Keeps a tally of the nearest point passed in and returns it with GetOutput.
    Also keeps a pointer to the nearest candidate and a copy of the nearest
    point on that candidate, this data can be accessed by an adapter such as
    EvalXDist and EvalAngle.
    """
    def __init__(self, owner: WorldObject, range: float, Nmax: int = 3):
        """
        Initializes the EvalNearest object with the owner and range.

        Args:
            owner (WorldObject): The owner of the evaluation.
            range (float): The range within which to evaluate.
        """
        self.owner = owner
        self.range = range
        self.distances = []
        self.Nmax = Nmax

    def Reset(self):
        """
        Resets the evaluation to its initial state.
        """
        self.distances.clear()

    def __call__(self, obj: WorldObject, loc: Vector2D):
        """
        Performs the evaluation.

        Args:
            obj (WorldObject): The object being evaluated.
            loc (Vector2D): The location of the object.
        """
        distance = (self.owner.GetLocation() - loc).GetLength()

        if distance < self.range:
            self.distances.append(distance)

    def GetOutput(self) -> float:
        """
        Returns the output of the evaluation.

        Returns:
            float: The output value.
        """
        if len(self.distances) == 0:
            return 0

        # Only consider the Nmax nearest objects
        if len(self.distances) > self.Nmax:
            distances = np.sort(self.distances)
            distances = distances[:self.Nmax]
        else:
            distances = self.distances

        # Calculate proximity scores for each detected object
        proximityScores = np.zeros(len(distances))
        for i, distance in enumerate(distances):
            proximityScores[i] = 1.0 / (1 + np.abs(np.log10(distance)))

        return np.sum(proximityScores)

class ScaleCompose():
    """
    ScaleCompose allows the chaining of two scaling functions together, such
    the output of a ScaleCompose functor is the result of second(first(input)),
    where first and second are the arguments in ScaleCompose's constructor.
    For example, to create a function which scales the input from [0:50] to [0:1]
    and then adds random noise between -0.5 and +0.5:
    s->SetScalingFunction(new ScaleCompose(new ScaleLinear(50.0),
    new ScaleNoise(-0.5, 0.5)));
    To compose more complex functions, instances of ScaleCompose may be nested.
    ScaleCompose is responsible for deleting its child functions.
    """
    def __init__(self,
        first: SensorScaleFunction,
        second: SensorScaleFunction):
        """
        Initializes ScaleCompose object.

        Args:
            first (SensorScaleFunction): First scaling function.
            second (SensorScaleFunction): Second scaling function.
        """
        self.scaleFunctions = [first, second]

    def __call__(self, input: float) -> float:
        """
        Calls the scaling functions in order.

        Args:
            input (float): Input value.

        Returns:
            float: Output value after applying both scaling functions.
        """
        return self.second(self.first(input))


class ScaleLinear(SensorScaleFunction):
    """
    A simple linear scaling function which defaults to an input scale between
    0 and a defined maximum, scaling to an output range between 0 and 1. Any
    input and output range can be defined, including inverted ranges with
    min > max, which can invert the output.
    """

    def __init__(self,
        inputMinimum: float,
        inputMaximum: float,
        outputMinimum: float = 0.0,
        outputMaximum: float = 1.0):
        """
        Initializes ScaleLinear object with custom input and output ranges.

        Args:
            inputMinimum (float): Minimum value of the input range.
            inputMaximum (float): Maximum value of the input range.
            outputMinimum (float): Minimum value of the output range.
            outputMaximum (float): Maximum value of the output range.
        """
        self.inMin = inputMinimum
        self.inMax = inputMaximum
        self.outMin = outputMinimum
        self.outMax = outputMaximum

    def __call__(self, input: float) -> float:
        """
        Applies linear scaling to the input value.

        Args:
            input (float): Input value.

        Returns:
            float: Scaled output value.
        """
        return (input - self.inMin) / (self.inMax - self.inMin) * (self.outMax - self.outMin) + self.outMin


class ScaleAbs(SensorScaleFunction):
    def __call__(self, input: float) -> float:
        """
        Returns the absolute value of the input.

        Args:
            input (float): Input value.

        Returns:
            float: Absolute value of the input.
        """
        return input if input >= 0.0 else -input


class ScaleThreshold(SensorScaleFunction):
    """
    ScaleThreshold takes values: threshold, min, and max, and returns min if input < threshold,
    or max if input >= threshold. Min and max default to 0 and 1.
    """

    def __init__(self,
        threshold: float,
        minimum: float = 0.0,
        maximum: float = 1.0):
        """
        Initializes a ScaleThreshold object with the specified threshold, minimum, and maximum values.

        Args:
            threshold (float): The threshold value.
            minimum (float, optional): The minimum value. Defaults to 0.0.
            maximum (float, optional): The maximum value. Defaults to 1.0.
        """
        self.threshold = threshold
        self.minimum = minimum
        self.maximum = maximum

    def __call__(self, input: float) -> float:
        """
        Returns the minimum value if the input is less than the threshold, otherwise returns the maximum value.

        Args:
            input (float): The input value.

        Returns:
            float: The scaled output value.
        """
        return self.minimum if input < self.threshold else self.maximum

class ScaleNoise(SensorScaleFunction):
    """
    ScaleNoise adds uniform random noise to its input. Minimum and maximum
    values may be specified, but default to [-0.1:0.1]
    """

    def __init__(self,
        minimum: float = -0.1,
        maximum: float = 0.1):
        """
        Initializes a ScaleNoise object with the specified minimum and maximum values.

        Args:
            minimum (float, optional): The minimum value. Defaults to -0.1.
            maximum (float, optional): The maximum value. Defaults to 0.1.
        """
        self.minimum = minimum
        self.maximum = maximum

    def __call__(self, input: float) -> float:
        """
        Returns the input value plus uniform random noise between the minimum and maximum values.

        Args:
            input (float): The input value.

        Returns:
            float: The scaled output value with added noise.
        """
        return input + random.uniform(self.minimum, self.maximum)

class ScaleAdapter(SensorScaleFunction):
    """
    Allows any unary functor to be adapted for use as a scaling function.
    """

    def __init__(self, functor):
        """
        Initializes a ScaleAdapter object with the specified functor.

        Args:
            functor: The functor to be adapted.
        """
        self.functor = functor

    def __call__(self, input):
        """
        Calls the functor with the input value and returns the result.

        Args:
            input (double): The input value to be scaled.

        Returns:
            double: The scaled output value.
        """
        return self.functor(input)