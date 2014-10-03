import numpy as np
import networkx as nx
import math
import random



def convert(something):#use networkx conversion from numpy array
    #g = nx.from_numpy_matrix(someNPMat)
    g = nx.to_networkx_graph(something)
    return g

def generateStochasticKron(initMat, k, directed=False, customEdges=False, edges=0):
    initN = initMat.getNumNodes()
    nNodes = math.pow(initN, k)#get final size and make empty 'kroned' matrix
    mtxDim = initMat.getNumNodes()
    mtxSum = initMat.getMtxSum()
    if(customEdges == True):
        nEdges = edges
        if(nEdges > (nNodes*nNodes)):
            raise ValueError("More edges than possible with number of Nodes")
    else:
        nEdges = math.pow(mtxSum, k) #get number of predicted edges
    collisions = 0

    print "Edges: "
    print nEdges
    print "Nodes: "
    print nNodes
    
    #create vector for recursive matrix probability
    probToRCPosV = []
    cumProb = 0.0
    for i in range(mtxDim):
        for j in range(mtxDim):
            prob = initMat.getValue(i, j)
            if(prob > 0.0):
                cumProb += prob
                probToRCPosV.append((cumProb/mtxSum, i, j))
                #print "Prob Vector Value:" #testing
                #print cumProb/mtxSum #testing

    #add Nodes
    finalGraph = np.zeros((nNodes, nNodes))
    #add Edges
    e = 0
    #print nEdges #testing
    while(e < nEdges):
        rng = nNodes
        row = 0
        col = 0
        for t in range(k):
            prob = random.uniform(0, 1)
            #print "prob:" #testing
            #print prob #testing
            n = 0
            while(prob > probToRCPosV[n][0]):
                n += 1
            mrow = probToRCPosV[n][1]
            mcol = probToRCPosV[n][2]
            rng /= mtxDim
            row += mrow * rng
            col += mcol * rng
        if(finalGraph[row, col] == 0): #if there is no edge
            finalGraph[row, col] = 1
            e += 1
            if(not directed): #symmetry if not directed
                if(row != col):
                    finalGraph[col, row] = 1
                    e += 1
        else:
            collisions += 1
    print "Collisions: "
    print collisions #testing  
    finalGraph = convert(finalGraph)
    return finalGraph
