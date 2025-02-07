# from built-in
import random
# from third-party
import numpy as np
# from pybeast
from pybeast.core.control.feedforwardnet import FeedForwardNet

def test_fire():

    N = 10000

    for _ in range(N):

        outputs = random.randint(1, 4)
        inputs = random.randint(1, 4)
        hiddens = random.randint(1, 10)
        bias = np.random.choice([True, False])

        inputValues = 2.0 * np.random.rand(inputs) - 1.0

        ffn = FeedForwardNet(inputs, outputs, hiddens, bias=bias)
        ffn.Randomise()
        ffn.SetInputs(inputValues)
        ffn.Fire()

        rows = hiddens
        cols = inputs + (1 if bias else 0)

        weighMatrix = np.zeros((rows, cols))

        for i, neuron in enumerate(ffn.hiddenLayer):
            weighMatrix[i, :] = neuron.weights

        if bias:
            inputValues = np.concatenate((inputValues, [1.0]))

        hidden_output = np.dot(weighMatrix, inputValues)
        hidden_output = ffn.ActivationFunction(hidden_output)

        rows = outputs
        cols = hiddens + (1 if bias else 0)

        weighMatrix = np.zeros((rows, cols))

        for i, neuron in enumerate(ffn.outputLayer):
            neuron = ffn.outputLayer[i]
            weighMatrix[i, :] = neuron.weights

        if bias:
            hidden_output = np.concatenate((hidden_output, [1.0]))

        output = np.dot(weighMatrix, hidden_output)
        output = ffn.ActivationFunction(output)

        assert np.allclose(output, ffn.outputValues)

    print("Passed 'test_FFN.test_fire!'")

    return

def test_set_config():

    N = int(1e3)

    for _ in range(N):

        outputs = random.randint(1, 4)
        inputs = random.randint(1, 4)
        hiddens = random.randint(1, 10)
        bias = np.random.choice([True, False])

        ffn = FeedForwardNet(inputs, outputs, hiddens, bias=bias)
        ffn.Randomise()
        config = ffn.GetConfiguration()
        ffn.SetConfiguration(config)
        newConfig = ffn.GetConfiguration()

        assert config == newConfig

    print("Passed 'test_FFN.test_set_config'!")

    return

if __name__ == '__main__':

    test_fire()
    test_set_config()