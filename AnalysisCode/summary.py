'''
timeStamp, agvTputA, avgTputB, medianA, medianB, fairness, 10percentileA, 90percentileA, 10percentileB, 90 percentileB, ccA, ccB
'''
import os
import sys
from matplotlib import pyplot as plt
import numpy

filename = 'AnalysisCode\\average_tput_per_run.csv'


class Flow:
    def __init__(self, cc, avgTput, median, tenth, ninetieth, fairness):
        self.cc = cc.replace('\n', '')
        self.avgTput = float(avgTput.replace('\n', ''))
        self.median = float(median.replace('\n', ''))
        self.tenth = float(tenth.replace('\n', ''))
        self.ninetieth = float(ninetieth .replace('\n', ''))
        self.fairness = float(fairness.replace('\n', ''))

    def setPartnerFlow(self, partner):
        self.partner = partner


class Protocal:
    def __init__(self, name):
        self.name = name
        self.flows = []
        self.average = 0
        self.FairnessCUBIC = []
        self.FairnessBBR = []
        self.FairnessHYBLA = []

    def addFlow(self, flow):
        self.flows.append(flow)

    def getFlows(self):
        return self.flows

    def computeAverage(self):
        total = 0
        for flow in self.flows:
            total += flow.avgTput
        self.average = total/len(self.flows)
        return self.average

    def computeAverageFairness(self):
        cubicTotalFairness = 0
        bbrTotalFairness = 0
        hyblaTotalFairness = 0
        for flow in self.flows:
            if flow.partner.cc == 'bbr':
                self.FairnessBBR.append(flow.fairness)
            elif flow.partner.cc == 'cubic':
                self.FairnessCUBIC.append(flow.fairness)
            elif flow.partner.cc == 'hybla':
                self.FairnessHYBLA.append(flow.fairness)
        # if self.name == 'cubic':
        #     self.FairnessCUBIC = [0]
        # elif self.name == 'bbr':
        #     self.FairnessBBR = [0]
        # elif self.name == 'hybla':
        #     self.FairnessHYBLA = [0]


class Summary:
    def __init__(self):
        self.cubic = Protocal(name='cubic')
        self.bbr = Protocal(name='bbr')
        self.hybla = Protocal(name='hybla')
        self.protocols = [self.cubic, self.bbr, self.hybla]

    def organize(self):
        file = open(filename, "r")
        for line in file:
            fields = line.split(',')
            a = Flow(cc=fields[-2], avgTput=fields[1], median=fields[3],
                     tenth=fields[6], ninetieth=fields[7], fairness=fields[5])
            b = Flow(cc=fields[-1], avgTput=fields[2], median=fields[4],
                     tenth=fields[8], ninetieth=fields[9], fairness=fields[5])
            pair = [a, b]
            a.setPartnerFlow(partner=b)
            b.setPartnerFlow(partner=a)
            for p in pair:
                if p.cc == 'cubic':
                    self.cubic.addFlow(flow=p)
                if p.cc == 'bbr':
                    self.bbr.addFlow(flow=p)
                if p.cc == 'hybla':
                    self.hybla.addFlow(flow=p)

    def plotSummaries(self):
        mean = []
        ten = []
        ninety = []
        median = []
        labels = []
        for p in self.protocols:
            localMean = []
            localTen = []
            localNinety = []
            localMedian = []
            labels.append(p.name)
            for flow in p.flows:
                localMean.append(flow.avgTput)
                localTen.append(flow.tenth)
                localNinety.append(flow.ninetieth)
                localMedian.append(flow.median)
            mean.append(localMean)
            ten.append(localTen)
            ninety.append(localNinety)
            median.append(localMedian)

        fig1, means = plt.subplots()
        means.set_xticklabels(labels)
        means.set_title(
            'Average Throughput Distribution per\nCongestion Control Protocol')
        #plt.ylim([20, 35])
        means.boxplot(mean, showfliers=False)
        means.set_ylabel("Throughput (Mbits)")
        means.set_xlabel("Protocol")
        fig2, medians = plt.subplots()
        medians.set_xticklabels(labels)
        medians.set_title(
            'Median Throughput Distribution per\nCongestion Control Protocol')
        #plt.ylim([20, 35])
        medians.boxplot(median, showfliers=False)
        medians.set_ylabel("Throughput (Mbits)")
        medians.set_xlabel("Protocol")
        fig3, tens = plt.subplots()
        tens.set_xticklabels(labels)
        tens.set_title(
            'Tenth Percentile Throughput Distribution per\nCongestion Control Protocol')
        #plt.ylim([20, 35])
        tens.boxplot(ten, showfliers=False)
        tens.set_ylabel("Throughput (Mbits)")
        tens.set_xlabel("Protocol")
        fig3, nineties = plt.subplots()
        nineties.set_xticklabels(labels)
        nineties.set_title(
            'Ninetieth Percentile Throughput Distribution per\nCongestion Control Protocol')
        #plt.ylim([20, 45])
        nineties.boxplot(ninety, showfliers=False)
        nineties.set_ylabel("Throughput (Mbits)")
        nineties.set_xlabel("Protocol")

    def plotFairness(self):
        fig1, cubicFairness = plt.subplots()
        fig2, bbrFairness = plt.subplots()
        fig3, hyblaFairness = plt.subplots()
        for p in self.protocols:
            p.computeAverageFairness()
            if p.name == 'cubic':
                cubicFairness.set_title(
                    f'Fairness Distribution CUBIC vs X')
                cubic = [p.FairnessCUBIC, p.FairnessBBR, p.FairnessHYBLA]
                cubicFairness.set_xticklabels(['cubic', 'bbr', 'hybla'])
                cubicFairness.boxplot(cubic, showfliers=False)
                cubicFairness.set_ylabel("Fairness Score")
                cubicFairness.set_xlabel("Protocol")
            elif p.name == 'bbr':
                bbrFairness.set_title(f'Fairness Distribution BBR vs X')
                bbr = [p.FairnessCUBIC, p.FairnessBBR, p.FairnessHYBLA]
                bbrFairness.set_xticklabels(['cubic', 'bbr', 'hybla'])
                bbrFairness.boxplot(bbr, showfliers=False)
                bbrFairness.set_ylabel("Fairness Score")
                bbrFairness.set_xlabel("Protocol")
            elif p.name == 'hybla':
                hyblaFairness.set_title(f'Fairness Distribution HYBLA vs X')
                hybla = [p.FairnessCUBIC, p.FairnessBBR, p.FairnessHYBLA]
                hyblaFairness.set_xticklabels(['cubic', 'bbr', 'hybla'])
                hyblaFairness.boxplot(hybla, showfliers=False)
                hyblaFairness.set_ylabel("Fairness Score")
                hyblaFairness.set_xlabel("Protocol")
        plt.show()

    def printSummaries(self):
        for p in self.protocols:
            print(f"{p.name}:{p.computeAverage()}")


def main():
    s = Summary()
    s.organize()
    s.plotSummaries()
    s.plotFairness()


if __name__ == '__main__':
    main()
