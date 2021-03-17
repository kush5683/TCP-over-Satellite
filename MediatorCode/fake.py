def runTrials(n):
    pass
def generateStats():
    pass
def setupHosts():
    pass
def cleanUp():
    pass
def startIperfServers(hosts):
    pass
def startTcpdump():
    pass
def startIperfClient():
    pass
def killCommands():
    pass
def transferPcaps():
    pass
def pcapToCSV():
    pass
def parseCSV():
    pass
def graph():
    pass
n = 0
hosts = 0














class mainScript:
    trials = [
                ['cubic', 'bbr'],
                ['cubic', 'hybla'],
                ['bbr', 'hybla'],
            ]

    runTrials(n)
    generateStats()

class singleTrial:
    available_hosts = {
            "cubic" : "mlcneta.cs.wpi.edu",
            "bbr"   : "mlcnetc.cs.wpi.edu",
            "hybla" : "mlcnetc.cs.wpi.edu",
            "dynamic"  : "mlcnetd.cs.wpi.edu" 
        }
    setupHosts()
    cleanUp()
    startIperfServers(hosts)
    startTcpdump()
    startIperfClient()
    killCommands()
    transferPcaps()

class graphing:
    pcapToCSV()
    parseCSV()
    graph()
    