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
        means.boxplot(mean, notch='True', showfliers=False)

        # fig2, medians = plt.subplots()
        # medians.set_xticklabels(labels)
        # medians.set_title(
        #     'Median Throughput Distribution per\nCongestion Control Protocol')
        # medians.boxplot(median, notch='True', showfliers=False)
        # fig3, tens = plt.subplots()
        # tens.set_xticklabels(labels)
        # tens.set_title(
        #     'Tenth Percentile Throughput Distribution per\nCongestion Control Protocol')
        # tens.boxplot(ten, notch='True', showfliers=False)
        # fig3, nineties = plt.subplots()
        # nineties.set_xticklabels(labels)
        # nineties.set_title(
        #     'Ninetieth Percentile Throughput Distribution per\nCongestion Control Protocol')
        # nineties.boxplot(ninety, notch='True', showfliers=False)

    def plotFairness(self):
        fig1, (cubicFairness, bbrFairness, hyblaFairness) = plt.subplots(3)
        for p in self.protocols:
            p.computeAverageFairness()
            if p.name == 'cubic':
                cubicFairness.set_title(
                        f'Fairness Distribution CUBIC vs X')
                cubic = [p.FairnessCUBIC,p.FairnessBBR, p.FairnessHYBLA]
                cubicFairness.set_xticklabels(['cubic','bbr','hybla'])
                cubicFairness.boxplot(cubic,notch='True', showfliers=False)
            elif p.name == 'bbr':
                bbrFairness.set_title(f'Fairness Distribution BBR vs X')
                bbr = [p.FairnessCUBIC,p.FairnessBBR, p.FairnessHYBLA]
                bbrFairness.set_xticklabels(['cubic','bbr','hybla'])
                bbrFairness.boxplot(bbr,notch='True', showfliers=False)
            elif p.name == 'hybla':
                hyblaFairness.set_title(f'Fairness Distribution HYBLA vs X')
                hybla = [p.FairnessCUBIC,p.FairnessBBR, p.FairnessHYBLA]
                hyblaFairness.set_xticklabels(['cubic','bbr','hybla'])
                hyblaFairness.boxplot(hybla,notch='True', showfliers=False)
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
