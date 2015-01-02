''' A series of functions that return a graph

'''


import random
import math
import networkx as nx

def get_graph(objects, properties):
    graph_type = properties['graph_type']
    n = len(objects)-1
    if 'num_nodes_to_attach' in properties.keys():
        k = properties['num_nodes_to_attach']
    else:
        k = 3
    r = properties['connection_probability']

    tries = 0
    while(True):
        if graph_type == 'random':
            x = nx.fast_gnp_random_graph(n,r)
        elif graph_type == 'erdos_renyi_graph':
            x = nx.erdos_renyi_graph(n,r)
        elif graph_type == 'watts_strogatz_graph':
            x = nx.watts_strogatz_graph(n, k, r)
        elif graph_type == 'newman_watts_strogatz_graph':
            x = nx.newman_watts_strogatz_graph(n, k, r)
        elif graph_type == 'barabasi_albert_graph':
            x = nx.barabasi_albert_graph(n, k, r)
        elif graph_type == 'powerlaw_cluster_graph':
            x = nx.powerlaw_cluster_graph(n, k, r)
        elif graph_type == 'cycle_graph':
            x = nx.cycle_graph(n)
        else: ##Star by default
            x = nx.star_graph(len(objects)-1)
        tries += 1
        cc_conn = nx.connected_components(x)
        if len(cc_conn) == 1 or tries > 5: 
            ##best effort to create a connected graph!
            break
    return x, cc_conn

def create_graph_type(objects, properties):
    (x, cc_conn) = get_graph(objects, properties)
    cc = nx.closeness_centrality(x)
    bc = nx.betweenness_centrality(x)
    deg = nx.degree_centrality(x)

    stats = {'cc':cc, 'bc':bc, 'deg':deg, \
             'num_cc':len(cc_conn), 'largest_cc':len(cc_conn[0])}

    conn = nx.Graph()
    for (i,j) in x.edges():
        inode = objects[i]
        jnode = objects[j]
        conn.add_edge(inode, jnode)
    return conn, stats

def random_directed_graph(objects, p):
    conn = nx.DiGraph()
    for object1 in objects:
        for object2 in objects:
            if random.random() <= p:
                conn.add_edge(object1,object2)
    return conn


def random_undirected_graph(objects, p):
    conn = nx.Graph()
    for object1 in objects:
        for object2 in objects:
            if random.random() <= 1-math.sqrt(1-p):
                conn.add_edge(object1,object2)
    return conn


def spatial_random_graph(objects, radius=1):
    ## objects is a list of objects of type
    ## first assign objects a location on a 1x1 board
    locs = {}
    for object in objects:
        x = random.random()
        y = random.random()
        locs[object] = (x,y)
    ## now determine connectivity between objects based on the input radius
    conn = nx.Graph()
    for object1 in objects:
        for object2 in objects:
            (x1,y1) = locs[object1]
            (x2,y2) = locs[object2]
            if math.sqrt( (x1-x2)**2 + (y1-y2)**2 ) <= radius:
                conn.add_edge(object1,object2)
    return conn

def collaborative_graph(objects):
    conn = nx.DiGraph()
    counter = 0
    ##Link bottom layer to middle layer
    for object in objects[5:]:
        conn.add_edge(object,objects[counter+1])
        conn.node[object]['rank'] = 2
        counter = (counter + 1) % 4

    ##Add collaboration between bottom row.
    for i in range(len(objects)/4):
        object1 = random.choice(objects[5:])
        object2 = random.choice(objects[5:])
        while object2 == object1:
            object2 = random.choice(objects[5:])
        conn.add_edge(object1,object2)
        conn.add_edge(object2,object1)
                 
    ##Add collaboration between middle row.
    for object1 in objects[1:5]:
        for object2 in objects[1:5]:
            if object1 != object2:
                conn.add_edge(object1,object2)
                conn.add_edge(object2,object1)
                 
    ##Link middle layer to root
    for object in objects[1:5]:
        conn.node[object]['rank'] = 1
        conn.add_edge(object,objects[0])
    conn.node[objects[0]]['rank'] = 0
            
    return conn

def hierarchy_graph(objects):
    conn = nx.DiGraph()
    counter = 0
    ##Link bottom layer to middle layer
    for object in objects[5:]:
        conn.add_edge(object,objects[counter+1])
        conn.node[object]['rank'] = 2
        counter = (counter + 1) % 4

    ##Link middle layer to root
    for object in objects[1:5]:
        conn.add_edge(object, objects[0])
        conn.node[object]['rank'] = 1
    conn.node[objects[0]]['rank'] = 0

    return conn

