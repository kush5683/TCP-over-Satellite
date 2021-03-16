import os
import subprocess
import sys
import time
from trial import Trial


class Experiment:
    def __init__(self, batchNum, user='kshah2', data='3k'):
        self.batchNum = batchNum
        self.user = user
        self.graphCommands = []
        self.data = data

    def oneTimeSetup(self):
        sshPrefix = f'ssh {self.user}@glomma.cs.wpi.edu'
        proxy = f'./setProxy.sh 3'
        routes = f'./setup_routes'
        commands = [proxy, routes]
        for command in commands:
            os.system(f'{sshPrefix} \"{command}\"')

    def graphCommandsFile(self, command):
        filename = f'{self.batchNum}-graph-commands.txt'
        f = open(filename, "a")
        f.write(f'{command}\n')
        f.close()

    def all_trials(self):
        # machine = {
        #         "mlcneta": "cubic",
        #         "mlcnetb": "cubic",
        #         "mlcnetc": "bbr",
        #         "mlcnetd": "pcc",
        #      }

        trials = [
            # ['cubic', 'cubic'],
            ['cubic', 'bbr'],
            ['cubic', 'hybla'],
            #['bbr', 'bbr'],
            ['bbr', 'hybla'],
            # ['hybla', 'hybla'],
        ]
        runNum = 0
        for i in range(1):
            print(f'Running batch #{i}')
            for t in trials:
                tr = Trial(data=self.data, cc=t, batchNum=self.batchNum,
                           runNum=runNum, timeout=450, log=True)
                self.graphCommandsFile(tr.start())
            runNum += 1

    def stats(self):
        filename = f'/users/kshah2/SatelliteCode/trial-{self.batchNum}/{self.batchNum}-graph-commands.txt'
        print(filename)
        f = open(filename, "r")
        for line in f:
            print(line)
            os.system(line)
            # list_of_commands = line.split()
            # print(list_of_commands)
            # command = subprocess.Popen(list_of_commands)
            # while command.poll() is None:
            #     pass


def main():
    e = Experiment(batchNum=201, data='500M')
    e.oneTimeSetup()
    time1 = time.time()
    e.all_trials()
    time2 = time.time()
    print(time2-time1)
    e.stats()


if __name__ == "__main__":
    main()
