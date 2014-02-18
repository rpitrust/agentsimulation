''' A series of functions that return a graph

'''


import random
import math
import networkx as nx

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
            if random.random() <= 1-sqrt(1-p):
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
    conn = nx.Graph()
    counter = 0
    ##Link bottom layer to middle layer
    for object in objects[5:]:
        conn.add_edge(object,objects[counter+1])
        conn.node[object]['rank'] = 2
        counter = (counter + 1) % 4

    ##Add collaboration between bottom row.
    for object1 in objects[1:5]:
        object2 = random.choice(objects[1:5])
        while object2 == object1:
            object2 = random.choice(objects[1:5])
        conn.add_edge(random.choice(conn.neighbors(object1)),
                 random.choice(conn.neighbors(object2)))
                 
    ##Add collaboration between middle row.
    for object1 in objects[1:5]:
        for object2 in objects[1:5]:
            if object1 != object2:
                conn.add_edge(object1,object2)
                 
    ##Link middle layer to root
    for object in objects[1:5]:
        conn.node[object]['rank'] = 1
        conn.add_edge(objects[0],object)
    conn.node[objects[0]]['rank'] = 0
            
    return conn

def hierarchy_graph(objects):
    conn = nx.Graph()
    counter = 0
    ##Link bottom layer to middle layer
    for object in objects[5:]:
        conn.add_edge(object,objects[counter+1])
        conn.node[object]['rank'] = 2
        counter = (counter + 1) % 4

    ##Link middle layer to root
    for object in objects[1:5]:
        conn.add_edge(objects[0],object)
        conn.node[object]['rank'] = 1
    conn.node[objects[0]]['rank'] = 0

    return conn
