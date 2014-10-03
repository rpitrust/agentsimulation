import numpy as np

class InitMatrix():

    def __init__(self, numNodes, W=None):
        self.numNodes = numNodes
        #initially we will take in the number of nodes when the object is created

    def getNumNodes(self):
        return self.numNodes

    def setNumNodes(self, v):
        self.numNodes = v

    def getValue(self, node1, node2):
        return self.W[node1, node2]

    def setValue(self, newVal, node1, node2):
        self.W[node1, node2] = newVal

    def getMtxSum(self):
        n = self.getNumNodes()
        s = 0.0
        for i in range(n):
            for j in range(n):
                s += self.getValue(i, j)
        int(s)
        return s

    def make(self): #This makes a init matrix manual (user adds edges)
        n = self.numNodes #getNumNodes(self)
        initMat = np.zeros((n, n)) #Creates corret size of init matrix with all 0s
        self.W = initMat

    def makeStochastic(self, alpha, beta, selfloops=True):
        #parm check
        if (not(0.00 <= alpha <= 1.00)):
            raise IOError("alpha (arguement 1) must be a value equal to or between 0 and 1; it is a probability")
        if (not(0.00 <= beta <= 1.00)):
            raise IOError("beta (arguement 2) must be a value equal to or between 0 and 1; it is a probability")

        n = self.getNumNodes()

        #switch 1s and 0s for alpha and beta, keep self loops
        for i in range(n):
            for j in range(n):
                if (i == j):
                    if(selfloops):
                        continue
                elif (self.getValue(i, j) == 0):
                    self.setValue(beta, i, j)
                else:
                    self.setValue(alpha, i, j)

    def addEdge(self, node1, node2, edge=1):
        node1 = int(node1)
        node2 = int(node2)
        if edge == 0 or edge == float('inf'):
            raise ValueError("Cannot add a zero or infinite edge")

        self.W[node1, node2] = edge
