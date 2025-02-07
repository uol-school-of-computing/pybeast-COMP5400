# from built-in
import random
# from third-party
import numpy as np
# from pybeast
from pybeast.core.utils.vector2D import Vector2D
from pybeast.core.world.world import WORLD_DISP_PARAM
from pybeast.core.world.worldobject import WorldObject
from pybeast.core.agents.animat import Animat
from pybeast.core.sensors.sensor import ProximitySensor, NearestAngleSensor

width = WORLD_DISP_PARAM.width
height = WORLD_DISP_PARAM.height
diagonal = np.sqrt(width**2 + height**2)


def test_NearestAngle():

    for _ in range(int(1e3)):

        x = width * random.random()
        y = height * random.random()
        aniArr = np.array([x, y])
        aniOri = 2.0*np.pi*random.random()

        ani = Animat(startLocation =  Vector2D(x, y), startOrientation = aniOri)
        sensorRange = diagonal * random.random()
        ani.AddSensor('angle', NearestAngleSensor(WorldObject, sensorRange))
        ani.Init()

        numberObjects = 10
        objects = []
        objArr = np.zeros((numberObjects,2))

        for i in range(numberObjects):
            x, y = width * random.random(), height * random.random()
            location = Vector2D(x, y)
            obj = WorldObject(startLocation=location)
            obj.Init()
            objects.append(obj)
            objArr[i, :] = (x, y)

        for obj in objects:
            ani.sensors['angle'].Interact(obj)

        distanceArr = objArr - aniArr[None, :]
        distances = np.linalg.norm(distanceArr, axis = 1)
        idx = distances.argmin()

        # check if nearest object was correctly found
        if distances[idx] <= sensorRange:
            assert ani.sensors['angle'].EvalFunc.bestCandidate is objects[idx]
        else:
            assert  ani.sensors['angle'].EvalFunc.bestCandidate is None

        # check if correct relative angle was calculated
        if distances[idx] <= sensorRange:
            angle = np.arctan2(distanceArr[idx, 1], distanceArr[idx, 0])
            if angle < 0:
                angle += 2.0 * np.pi
            relAngleArr = angle - aniOri
            if relAngleArr > np.pi:
                relAngleArr -= 2.0*np.pi
            assert np.isclose(relAngleArr, ani.sensors['angle'].EvalFunc.GetOutput())
        else:
            assert ani.sensors['angle'].EvalFunc.GetOutput() == 0.0

    print("Passed 'test_sensors.test_NearestAngle'!")

def test_Proximity():

    for _ in range(int(1e3)):

        x = width * random.random()
        y = height * random.random()
        aniArr = np.array([x, y])
        aniOri = 2.0 * np.pi * random.random()

        ani = Animat(startLocation=Vector2D(x, y), startOrientation=aniOri, solid=False)
        sensorRange = diagonal * random.random()
        sensorScope = 2.0*np.pi*random.random()
        relSensorOrientation = random.uniform(-np.pi, np.pi)
        ani.AddSensor('beam', ProximitySensor(WorldObject, sensorScope, sensorRange, relSensorOrientation, simple=True))
        ani.Init()
        sensorArr = np.array([ani.sensors['beam'].location.x, ani.sensors['beam'].location.y])

        assert np.allclose(sensorArr, aniArr)

        numberObjects = 5
        objects = []
        objArr = np.zeros((numberObjects, 2))

        for i in range(numberObjects):
            x, y = width * random.random(), height * random.random()
            location = Vector2D(x, y)
            obj = WorldObject(startLocation=location)
            obj.Init()
            objects.append(obj)
            objArr[i, :] = (x, y)

        distanceVecMat = objArr - sensorArr[None, :]
        distanceArr = np.linalg.norm(distanceVecMat, axis=1)

        for obj in objects:
            ani.sensors['beam'].Interact(obj)

        sensorOri = aniOri + relSensorOrientation
        if sensorOri < 0:
            sensorOri += 2.0*np.pi
        sensorOri = sensorOri % (2*np.pi)

        startAngle = sensorOri - 0.5 * sensorScope
        endAngle = sensorOri + 0.5 * sensorScope

        if startAngle < 0:
            startAngle += 2 * np.pi
        endAngle = endAngle % (2*np.pi)

        idx_arr = np.argsort(distanceArr)
        distanceArr  = distanceArr[idx_arr]
        distanceVecMat = distanceVecMat[idx_arr]

        for idx, distance, distanceVec in zip(idx_arr, distanceArr, distanceVecMat):

            # check if correct relative angle was calculated
            if distance <= sensorRange:
                angle = np.arctan2(distanceVec[1], distanceVec[0])
                if angle < 0:
                    angle += 2*np.pi

                # If the scope does not cross 0 degrees
                if startAngle < endAngle:
                    inscope = startAngle <= angle <= endAngle
                # If the scope crosses 0 degrees
                else:
                    inscope = startAngle <= angle or angle <= endAngle

                if inscope:
                    assert ani.sensors['beam'].EvalFunc.bestCandidate is objects[idx]
                    break
            else:
                ani.sensors['beam'].EvalFunc.bestCandidate is None

    print("Passed 'test_sensors.test_Proximity'!")


if __name__ == '__main__':

    #test_NearestAngle()
    test_Proximity()
