import time

class Profiler():

    def __init__(self):
        self.functionsToProfile = {}

        for functionName in [
            'Simulation.Update',
            'Simulation.EndGeneration',
            'animat.Interact',
            'animat.Interact.withObjects',
            'animat.Interact.withAnimats',
            'animat.Interact.withObjects.Sensor.Interact',
            'animat.Interact.withObjects.Collision']:

            self.functionsToProfile[functionName] = {'count': 0, 'times': []}

    def Start(self):
        self.startTime = time.time()

    def End(self):
        endTime = time.time()
        self.runTime = endTime - self.startTime

    def Report(self):

        totalTimes = [sum(profile['times']) for profile in self.functionsToProfile.values()]
        avgTimes = [sum(profile['times'])/len(profile['times']) for profile in self.functionsToProfile.values()]

        print(f"Total runtime: {self.runTime}")

        for i, (name, profile) in enumerate(self.functionsToProfile.items()):
            print(
                f"{name}: "
                f"number of counts: {profile['count']}, \n"
                f"average runtime: {avgTimes[i]}, \n"
                f"total runtime: {totalTimes[i]}, \n"
                f"total relative runtime: {totalTimes[i] / self.runTime} \n"
            )










