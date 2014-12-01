''' Returns a Kronecker Graph for Agent Simulations using BH Kronecker Generator Package

'''
#like graphgen but only for kronecker -BH

import random
import math
import networkx as nx
from KroneckerInitMatrix import InitMatrix
import KroneckerGenerator
import numpy as np
    

def create_graph_stats(graph):
    
    cc_conn = nx.connected_components(graph) #How is this a generator object!?
    num_cc = nx.number_connected_components(graph)
    #largest_cc = len(cc_conn[0])
    
    cc = nx.closeness_centrality(graph)
    bc = nx.betweenness_centrality(graph)
    deg = nx.degree_centrality(graph)
    dens = nx.density(graph)

    stats = {'cc':cc, 'bc':bc, 'deg':deg, \
             'num_cc':num_cc, 'dens':dens}#, 'largest_cc':largest_cc}
    
    return stats

def create_graph_kronecker(objects, properties): #uses alpha-beta method to build kron
    initEdges = properties['init_edges']
    alpha = properties['alpha']
    beta = properties['beta']
    k = properties['kron_interations']
    tryAgain = True
    init = InitMatrix(properties['kron_seed_nodes'])
    init.make()
    init.addSelfEdges()
    for i in range(len(initEdges)):
        pos = initEdges[i]
        index1 = pos[0]
        index2 = pos[1]
        if(index1 > properties['kron_seed_nodes'] or index2 > properties['kron_seed_nodes']):
            raise IOError("init_edges are out of range of seed matrix size")
        else:
            init.addEdge(index1, index2)
            
    if(properties['kron_seed_self_loops_stochastic'] == False):
        init.makeStochasticAB(alpha, beta, False)
    else:
        init.makeStochasticAB(alpha, beta)
        
    while(tryAgain == True): #loop to make sure we are connected, should there be a limit to this?
        final = KroneckerGenerator.generateStochasticKron(init, k, True)
        is_conn = nx.is_connected(final) 
        if(is_conn == False):
            print "Graph was not connected, trying again..."
            tryAgain = True
        else:
            tryAgain = False

    stats = create_graph_stats(final)
    conn = nx.Graph()
    for (i,j) in final.edges():
        inode = objects[i]
        jnode = objects[j]
        conn.add_edge(inode, jnode)
    return conn, stats
