from datetime import time, tzinfo, datetime
import matplotlib
from numpy import average
import pandas as pd
from matplotlib import pyplot as plt
import sys
import os
import csv
import statistics
import numpy


if len(sys.argv) != 9:
    print("argument miss-match")
    exit()


class Grapher:
    def __init__(self, cc, hostA, hostB, timeStamp, batchNum, runNum, printFrequency=1000, sim_time=1):
        self.cc = cc
        self.hostA = hostA
        self.hostB = hostB
        self.timeStamp = timeStamp
        self.batchNum = batchNum
        self.runNum = runNum
        self.printFrequency = printFrequency
        self.sim_time = sim_time
        self.hostA_times_raw = pd.to_datetime(
            hostA['frame.time'], infer_datetime_format=True)
        self.hostB_times_raw = pd.to_datetime(
            hostB['frame.time'], infer_datetime_format=True)
        self.hostA_times = []
        self.hostB_times = []
        self.hostA_time_since_start = []
        self.hostB_time_since_start = []
        self.hostA_seconds = []
        self.hostB_seconds = []
        self.hostA_tput = []
        self.hostB_tput = []
        self.hostA_bytes_sent = 0
        self.hostB_bytes_sent = 0

    def computeTimeSinceStart(self):
        for i in range(len(self.hostA_times_raw)):
            hostA_td = pd.Timedelta(
                str(self.hostA_times_raw[i]-self.hostA_times_raw[0]))
            self.hostA_time_since_start.append(
                hostA_td.seconds + (hostA_td.microseconds / 1000000) + (hostA_td.nanoseconds / 1000000000))
            if(i % self.printFrequency == 0):
                print(f'On frame #{i} of hostA')

        for i in range(len(self.hostB_times_raw)):
            hostB_td = pd.Timedelta(
                str(self.hostB_times_raw[i]-self.hostB_times_raw[0]))
            self.hostB_time_since_start.append(
                hostB_td.seconds + (hostB_td.microseconds / 1000000) + (hostB_td.nanoseconds / 1000000000))
            if(i % self.printFrequency == 0):
                print(f'On frame #{i} of hostB')

    def computeTput(self):
        for i in range(len(self.hostA['frame.len'])):
            if(i % self.printFrequency == 0):
                print(f'On frame #{i} of hostA')
            if self.hostA_time_since_start[i] <= float(self.sim_time):
                self.hostA_bytes_sent += self.hostA['frame.len'][i]
            else:
                while self.hostA_time_since_start[i] >= self.sim_time:
                    self.hostA_tput.append((self.hostA_bytes_sent*8)/1000000)
                    self.hostA_bytes_sent = 0
                    self.hostA_seconds.append(self.sim_time)
                    self.sim_time += 1
                self.hostA_bytes_sent += self.hostA['frame.len'][i]

        self.sim_time = 1

        for i in range(len(self.hostB['frame.len'])):
            if(i % self.printFrequency == 0):
                print(f'On frame #{i} of hostB')
            if self.hostB_time_since_start[i] <= float(self.sim_time):
                self.hostB_bytes_sent += self.hostB['frame.len'][i]
            else:
                while self.hostB_time_since_start[i] >= self.sim_time:
                    self.hostB_tput.append((self.hostB_bytes_sent*8)/1000000)
                    self.hostB_bytes_sent = 0
                    self.hostB_seconds.append(self.sim_time)
                    self.sim_time += 1
                self.hostB_bytes_sent += self.hostB['frame.len'][i]

    def outputGraph(self):
        fig = plt.figure(figsize=[18, 9])
        colors = []
        print(self.cc)
        for c in range(len(self.cc)):
            print(self.cc[c])
            if self.cc[c] == 'cubic':
                colors.append('green')
            elif self.cc[c] == 'bbr':
                colors.append('blue')
            elif self.cc[c] == 'hybla':
                colors.append('orange')
        print(colors)
        plt.plot(self.hostA_seconds, self.hostA_tput, color=colors[0])
        plt.plot(self.hostB_seconds, self.hostB_tput, color=colors[1])
        plt.xlabel("Time (seconds)")
        plt.ylabel("Throughput (Mbits)")
        legendA = f'{self.cc[0]}'
        legendB = f'{self.cc[1]}'
        plt.legend([legendA, legendB])
        plt.title('Throughput vs Time')
        filename = f'graphs/trial-{self.batchNum}/{self.cc[0]}-{self.cc[1]}-run{self.runNum}-{self.timeStamp}-throughput-vs-time.png'
        plt.savefig(filename, dpi=100)

    def saveStats(self):
        agvTputA = sum(self.hostA_tput) / len(self.hostA_tput)
        agvTputB = sum(self.hostB_tput) / len(self.hostB_tput)
        fairness = agvTputA - agvTputB
        stats = open(
            f'stats/trial-{self.batchNum}/average_tput_per_run.csv', 'a')
        print("Appending statistics to csv")
        stats.write(
            f'{self.timeStamp},{agvTputA},{agvTputB},{statistics.median(self.hostA_tput)},{statistics.median(self.hostB_tput)},{fairness},{numpy.percentile(self.hostA_tput,10)},{numpy.percentile(self.hostA_tput,90)},{numpy.percentile(self.hostB_tput,10)},{numpy.percentile(self.hostB_tput,90)},{self.cc[0]},{self.cc[1]}\n')
        stats.close()

    def graph(self):
        print("Running computeTimesSinceStart()")
        self.computeTimeSinceStart()
        print("Running computeTput()")
        self.computeTput()
        print("Running graph()")
        self.outputGraph()
        print("Running saveStats()")
        self.saveStats()
        # exit()


csvs = []


def pcapToCsv(pcaps, hosts, batchNum):
    csvsGenerated = 0
    for file in pcaps:
        host = f'{hosts[csvsGenerated]}'
        dirs = file.split('/')
        csvFilename = f"{dirs[0]}/csv/{dirs[2]}/{dirs[-1].split('.')[0]}.csv"
        #csvFilename = file.split('.')[0] + '.csv'
        print(file)
        print(csvFilename)
        tshark = f'tshark -r {file} -T fields \
                -e frame.number \
                -e frame.len \
                -e tcp.window_size \
                -e ip.src \
                -e ip.dst \
                -e tcp.srcport \
                -e tcp.dstport \
                -e frame.time \
                -E header=y \
                -E separator=, \
                -E quote=d \
                -E occurrence=f \
                > {csvFilename}'
        fullCommand = f'{tshark}'
        csvs.append(csvFilename)
        print(f'\trunning command: \n{fullCommand}')
        #timeStamp = self.getTimeStamp()
        os.system(fullCommand)
        #self.commandsRun.append((timeStamp, fullCommand))
        csvsGenerated += 1
        # self.sleep(5)


def main():
    batchNum = sys.argv[5]
    pcapToCsv(pcaps=[sys.argv[1], sys.argv[2]], hosts=[
              sys.argv[7], sys.argv[8]], batchNum=batchNum)
    print(csvs)
    hostA = pd.read_csv(csvs[0])  # csv for host a
    hostB = pd.read_csv(csvs[1])  # csv for host b
    os.chdir(os.path.expanduser("~/figures"))
    cc = [sys.argv[3], sys.argv[4]]
    runNum = sys.argv[6]
    # extract timestamp from csv filename
    timeStamp = csvs[0].split('/')[-1][8:-4]
    print(f'{cc}')
    g = Grapher(cc=cc, hostA=hostA, hostB=hostB,
                batchNum=batchNum, runNum=runNum, timeStamp=timeStamp)
    g.graph()
    print('All done')
    exit()


if __name__ == "__main__":
    main()
