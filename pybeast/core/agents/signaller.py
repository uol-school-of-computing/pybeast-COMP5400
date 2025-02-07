from abc import ABC, abstractmethod

import random
from typing import TypeVar, Dict, Any

class Signaller():
    """
    A general-purpose class for modelling signallers with discrete signal and state types.
    Signallers can be made to keep track of signalling costs and are compatible with their own signal sensor functions
    (if multiply inherited with WorldObject).
    Each Signaller template maintains its own static costs map, so costs are shared between signallers
    with the same templated types.
    """
    # These need to overwritten by child classes, otherwise all child classes will share the same Cost, Signal and State
    Cost = None
    Signal = None
    State = None

    def __init__(self):

        self.totalCost = 0
        self.state = None
        self.signals = {}

    def Reset(self):
        """Resets the Signaller by putting the total cost back to 0."""
        self.totalCost = 0.0

    def PushCost(self):
        """Adds the current signalling cost to the total signalling cost so far."""
        self.totalCost += self.GetCost()

    def GetState(self) -> State:
        """Returns the internal state of the signaller."""
        return self.state

    def GetSignal(self, s: State = None) -> Signal:
        """Returns the current signal."""
        if s is None:
            return self.signals.get(self.state)
        return self.signals.get(s)

    def GetCost(self) -> Cost:
        """Returns the current signalling cost."""
        return self.costs.get(self.state, {}).get(self.GetSignal(), Cost(0))

    @staticmethod
    def GetCost(st: State, si: Signal) -> Cost:
        """Returns the signalling cost for the specified state/signal."""
        return Signaller.costs.get(st, {}).get(si, Cost(0))

    def GetTotalCost(self) -> Cost:
        """Returns the total signalling cost so far."""
        return self.totalCost

    def SetState(self, s: State):
        """Sets the internal state of the signaller."""
        self.state = s

    def SetSignal(self, st: State, si: Signal):
        """Sets up the signals for each state."""
        self.signals[st] = si

    @staticmethod
    def SetCost(st: State, si: Signal, co: Cost):
        """Sets up costs associated with signalling."""
        if st not in Signaller.costs:
            Signaller.costs[st] = {}
        Signaller.costs[st][si] = co

    def Randomise(self, numStates: int, numSignals: int):
        """
        Randomises the signaller so that each possible internal state has a random signal associated with it.
        Also sets the signaller to a random state value.
        """
        self.signals.clear()
        for i in range(numStates):
            self.signals[State(i)] = Signal(random.randint(0, numSignals - 1))
        self.state = State(random.randint(0, numStates - 1))


class EvalNearestSignal:
    """
    Sensor evaluation functor: returns the signal of the nearest individual.
    """

    def __init__(self, o: Any, range: float):
        self.o = o
        self.range = range

    def GetOutput(self) -> float:
        """
        Returns the signal number (as a double) of the nearest signaller, or
        0.0 if no signaller was found (or the signaller is signalling 0)
        """
        s = self.o
        if isinstance(s, Signaller):
            return float(s.GetSignal())
        return 0.0


def NearestSignalSensor(highestSignal: int):
    """
    Constructs and returns a pointer to a sensor which will return the signal
    of the nearest Signaller of the specified type.
    """
    s = Sensor((0.0, 0.0), 0.0)
    s.SetMatchingFunction(MatchKindOf)
    s.SetEvaluationFunction(EvalNearestSignal(s, 1000.0))
    s.SetScalingFunction(ScaleLinear(0.0, float(highestSignal), -1.0, 1.0))
    return s
