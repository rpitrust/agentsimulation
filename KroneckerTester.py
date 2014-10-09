from InitMatrix import InitMatrix
import Generator
import numpy as np
import networkx as nx
import testgg as test

def get_graph(nxgraph):
    
    x = nxgraph
    cc_conn = nx.connected_components(x)
    num_cc = nx.number_connected_components(x)
    #largest_cc = len(cc_conn[0])

    return x, cc_conn, num_cc#, largest_cc

def create_graph_stats(nxgraph):
    (x, cc_conn, num_cc) = get_graph(nxgraph) #, largest_cc
    cc = nx.closeness_centrality(x)
    bc = nx.betweenness_centrality(x)
    deg = nx.degree_centrality(x)

    stats = {'cc':cc, 'bc':bc, 'deg':deg, \
             'num_cc':num_cc} #, 'largest_cc':largest_cc

    return stats #conn,

#above are methods to make input for histogram
nodes = 4
init = InitMatrix(nodes)
init.make()
#init.addEdge(0, 1)
#init.addEdge(0, 2)
#init.addEdge(0, 3)
#for i in range(nodes):
#        init.addEdge(i, i)#self edges
p = .45
c = 2
probArr = np.array([1, p*c, p*c, p*c, p*c, 1, p, p, p*c, p, 1, 0, p*c, p, 0, 1])
init.makeStochasticCustom(probArr) #pref attach

k = 3
print "Seed Matrix Nodes:"
print nodes
print "Kronecker Iterations:"
print k
nxgraph = Generator.generateStochasticKron(init, k, True)
#nx.draw_networkx(nxgraph) #not working?
#for line in nx.generate_edgelist(nxgraph, data=False):
 #   print(line)
print "Done Creating Network!"
print "Creating Histogram..."
histogramInput = create_graph_stats(nxgraph)
test.histogram(histogramInput, 25)
