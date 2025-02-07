# Built-in
import pickle
from random import random

# Third-party
import numpy as np

# This value decides the curve of the sigmoid function.
FFN_ACTIVATION_RESPONSE: float = 0.5;
# The width of columns in ToString output.
FFN_COLSIZE: int = 6;

class FFNeuron:
    """
    This member struct simply encapsulates the weighted sum function which
    has to be performed on the weights of each node when the net fires.
    """

    def __init__(self, n: int, bias: bool):

        self.weights = np.zeros(n + (1 if bias else 0))
        self.bias = bias

    def WeightedSum(self, values):

        if self.bias:
            return np.dot(self.weights[:-1], values) + self.weights[-1]
        else:
            return np.dot(self.weights, values)

class FeedForwardNet:
    """
    This is an implementation of a simple two-layer feed-forward neural network.
    """

    def __init__(self,
        inputs: int,
        outputs: int,
        hidden: int = 0,
        sig: bool = True,
        bias: bool = True):
        """
        Attributes:
            inputs (int): The number of inputs received by the net.
            outputs (int): The number of outputs the net produces.
            hidden (int): The number of nodes in the hidden layer.
            sigmoid (bool): Set to True (default) if a sigmoid ActivationFunction is used.
            biasNode (bool): Set to True (default) if each node is to have its own bias term.
            inputValues (List[float]): A vector storing the current input values.
            outputValues (List[float]): A vector storing the current output values.
            hiddenLayer (List[Neuron]): A vector of hidden layer neurons.
            outputLayer (List[Neuron]): A vector of output layer neurons.
        """
        self.Init(inputs, outputs, hidden, sig, bias)

    def __del__(self):
        pass

    def __str__(self):

        out = []

        out.append(f'Input values: {self.inputValues}')
        out.append('Hidden layer weights:')
        for i, neuron in enumerate(self.hiddenLayer):
            if self.biasNode:
                out.append(f'Neuron {i}: '
                    f'weights: {np.round(neuron.weights[:-1], 2)}, bias: {neuron.weights[-1]:.2f}')
            else:
                out.append(f'Neuron {i}: {np.round(neuron.weights[:-1], 2)}')

        out.append("Output layer weights:")

        for i, neuron in enumerate(self.outputLayer):
            if self.biasNode:
                out.append(f'Neuron {i}: '
                    f'weights: {np.round(neuron.weights[:-1], 2)}, bias: {neuron.weights[-1]:.2f}')
            else:
                out.append(f'Neuron {i}: {np.round(neuron.weights[:-1], 2)}')

        out.append("Output values:")
        out.append(self.outputValues)

        return '\n'.join(out)

    #================================================================================================
    # Class interface
    #================================================================================================

    def Init(self,
        inputs: int,
        outputs: int,
        hidden: int,
        sig: bool = True,
        bias: bool = True
        ):
        """
        Initializes the FeedForwardNet object with the specified dimensions and features.
            @param input: The number of inputs
            @param output: The number of outputs.
            @param hidden: The size of the hidden layer. If hid is 0 then the FFN acts as a perceptron.
            @param sig: Whether or not the net will use a sigmoid activation function. Defaults to True.
            @param bias: Whether each node has a bias value. Defaults to True.
        """

        self.inputs = inputs
        self.outputs = outputs
        self.hidden = hidden
        self.sigmoid = sig
        self.biasNode = bias
        self.inputValues = np.zeros(self.inputs)
        self.outputValues = np.zeros(self.outputs)

        self.numberInputToHiddenWeights = (self.inputs + (1 if self.biasNode else 0)) * self.hidden
        self.numberHiddenToOutputWeights = (self.hidden + (1 if self.biasNode else 0)) * self.outputs
        self.numberWeights = self.numberInputToHiddenWeights + self.numberHiddenToOutputWeights

        self.hiddenLayer = []
        self.outputLayer = []

        # For each hidden layer neuron, we instantiate a Neuron object.
        # The Neuron is initialized with the number of weights it needs,
        # which in this case is one per input. If biasNode has been set
        # to true, an extra weight is added. The use of this is explained
        # in the fire method.
        for _ in range(self.hidden):
            self.hiddenLayer.append(FFNeuron(self.inputs, self.biasNode))

        # If the hidden layer size is set to 0, normally that would break the
        # network but here I'm taking it to mean the net is a perceptron (one
        # layer of inputs, one layer of outputs, no hidden layer) and so the
        # output layer neurons have <inputs>, rather than <hidden>, inputs.
        if self.hidden == 0:
            self.hidden = self.inputs
        # Add one neuron per output value to the output layer, each with
        # one weight per hidden neuron (since this is the output layer,
        # inputs are coming from the hidden layer) and again an extra
        # weight if biasNode is set to true.
        for _ in range(outputs):
            self.outputLayer.append(FFNeuron(self.hidden, self.biasNode))

    def Fire(self) -> None:
        """
        This is the main method of the Feed Forward Network, where inputs are
        processed to calculate the output values. The Fire method assumes that
        inputs have previously been set using SetInput.
        """
        hiddenOutput = []  # A holding space for the output of the hidden layer, to pass to the output layer neurons.
        outputValues = []  # Store the output values

        # If the size of the hidden layer is set to 0, this particular ANN class
        # recognises that to mean there is no hidden layer, and so the input
        # values should be processed directly by the output layer.
        if self.hidden == 0:
            hiddenOutput = self.inputValues

        for neuron in self.hiddenLayer:
            output = neuron.WeightedSum(self.inputValues)
            # Apply activation function
            output = self.ActivationFunction(output)
            # Store output of hidden layer
            hiddenOutput.append(output)

        # Process the output layer
        for neuron in self.outputLayer:
            output = neuron.WeightedSum(hiddenOutput)
            # Apply activation function
            output = self.ActivationFunction(output)
            # Store output of output layer
            outputValues.append(output)

        # Update the output values
        self.outputValues = outputValues

    def Randomise(self):
        """
        Initializes every weight and bias in the net with a random number in the range [-1, 1].
        """
        for neuron in self.hiddenLayer:
            neuron.weights = np.random.uniform(-1.0, 1.0, size=len(neuron.weights))

        for neuron in self.outputLayer:
            neuron.weights = np.random.uniform(-1.0, 1.0, size=len(neuron.weights))

    def ActivationFunction(self, x: float) -> float:
        """
        The squashing function for the network, either a sigmoid or threshold function.
        :param n: The input value.
        :return: The output value.
        """
        if self.sigmoid:
            # Sigmoid function returns values between [-1.0, 1.0]
            return 2.0 / (1.0 + np.exp(-x / FFN_ACTIVATION_RESPONSE)) - 1.0
        else:
            # Threshold function
            return 1.0 if x > 0.0 else 0.0

    #================================================================================================
    # Setter and Getter
    #================================================================================================

    def SetActivationFunction(self, af: callable):
        setattr(self, 'ActivationFunction', callable)
        return

    def SetConfiguration(self, configs: dict):


        assert len(configs['hidden']) == self.hidden, \
            "configs number of hidden neurons is inconsistent with the network"
        assert len(configs['output']) == self.outputs, \
            "configs number of output neurons is inconsistent with the network"

        for neuron, weights in zip(self.hiddenLayer, configs['hidden']):
            assert len(weights) == len(neuron.weights), \
                'number of weights to hidden neuron is not the same as the number of inputs'
            neuron.weights[:] = weights

        for neuron, weights in zip(self.outputLayer, configs['output']):
            assert len(weights) == len(neuron.weights), \
                'number of weights to output neuron is not the same as the number of hidden neurons'
            neuron.weights[:] = weights

    def GetConfiguration(self) -> dict:
        """
        Returns all the weights and biases in the network as a list of floats,
        ideal for representing the network in an evolutionary algorithm.
        No information about the dimensions of the network is returned by this
        method - to return complete configuration data use Serialize.
        """
        # The configuration data contains no information about the
        # network's dimensions, bias nodes, or activation function.
        config = {
            'hidden': [neuron.weights for neuron in self.hiddenLayer],
            'output': [neuron.weights for neuron in self.outputLayer]
            }

        return config




    def SetInput(self, n: int, f: float):
        self.inputValues[n] = f

    def SetInputs(self, v: np.ndarray):
        self.inputValues[:] = v

    def GetOutput(self, n: int) -> float:
        return self.outputValues[n]

    def GetOutputs(self) -> np.ndarray:
        return self.outputValues

    def GetNumberInputs(self):
        return self.inputs

    def GetNumberNeurons(self):
        return self.outputs

    def GetNumberHidden(self):
        return self.hidden

    def IsSigmoid(self):
        return self.sigmoid

    def IsBiasNode(self):
        return self.biasNode

    def _GetInputValues(self):
        return self.inputValues

    def _GetOutputValues(self):
        return self.outputValues

    def _GetHiddenLayer(self):
        return self.hiddenLayer

    def _GetOutputLayer(self):
        return self.outputLayer

    def GetConfigurationLength(self):
        pass

    #================================================================================================
    # Serialization
    #================================================================================================

    def Serialise(self, out: str):
        """
        Serialize the FeedForwardNet object
        """
        #TODO: Implement serialization in a consistent manner throughout the project
        assert False, 'Not implemented yet'

    def Unserialise(inp):
        """
        Unserialize the FeedForwardNet object
        """
        # TODO: Implement serialization in a consistent manner throughout the project
        assert False, 'Not implemented yet'


