#Bens Version
import random
import math
import SimpleAgent 
import GraphGen as gg
import SimpleSimulationStats as ss
import networkx as nx
from simutil import * 
import simplejson as sj
import time
import sys
import KroneckerGenforSimulations as kg

def current_agent_stats (current_agent, stats):
    node_stats = {}
    node_stats['cc'] = stats['cc'][current_agent]
    node_stats['bc'] = stats['bc'][current_agent]
    node_stats['deg'] = stats['deg'][current_agent]
    #node_stats['dens'] = stats['dens'] #added from stats
    return node_stats

def balanced_node_sample(stats): #made by Ben
    """ Return 50 nodes balanced from top to bottom (25 from each), or all if less than 50 nodes in decreasing order
    of closeness centrality. 
    """
    balanced_list = []
    for key in stats['cc'].keys():
        balanced_list.append( (stats['cc'][key], key) )
    balanced_list.sort(reverse=True)
    nodes = [-1]
    num_to_extract_top = min(25, len(balanced_list))
    num_to_extract_bottom = min(25, (len(balanced_list) - num_to_extract_top))
    for (val, node) in balanced_list[: num_to_extract_top]:
        nodes.append(node)
    balanced_list.reverse();
    for (val, node) in balanced_list[: num_to_extract_bottom]:
        nodes.append(node)
    '''
    #test below
    print "Nodes Final"
    for i in range(len(nodes)):
        print nodes[i]
    #test above
    '''
    return nodes
    
def top_nodes (stats): #made by Sibel
    """ Return top 50, or all if less than 50 nodes in decreasing order
    of closeness centrality.
    """
    best_list = []
    for key in stats['cc'].keys():
        best_list.append( (stats['cc'][key], key) )
    best_list.sort(reverse=True)
    nodes = [-1]
    num_to_extract = min(50, len(best_list))
    for (val, node) in best_list[: num_to_extract]:
        nodes.append(node)
    '''
    #test below
    print "Nodes Final for top"
    for i in range(len(nodes)):
        print nodes[i]
    #test above
    '''
    return nodes

def add_to_output(all_results, results, outfile):
    all_results.append(results)
    if len(all_results) > 20:
        flush_results(all_results, outfile)

def flush_results(all_results, outfile):
    f = open(outfile,"a")
    for result in all_results:
        f.write( sj.dumps(result) + "\n")
    f.close()
    all_results = []


########## Run simulation
def one_step_simulation(agents):
    num_actions = 0
    actions_taken = []
    for agent in agents:
        actions_taken = agent.act()  ##list of (n, fact)
        for (n,fact) in actions_taken:
            num_actions += 1
            n.receive(fact, agent)
    return num_actions

def run_simulation_one_graph(properties, outfile):
    facts = range(properties['num_facts']+properties['num_noise'])
    agents = []
    all_results = []
    for i in xrange(properties['num_agents']):
        agents.append ( SimpleAgent.SimpleAgent(properties['willingness'],\
                                                properties['competence'],\
                                                properties['num_facts'],\
                                                properties['num_noise'],\
                                                properties['spamminess'],\
                                                properties['selfishness'],\
                                                properties['trust_used'],\
                                                properties['inbox_trust_used'],\
                                                properties['trust_filter_on'],
                                                twitter_model = properties['twitter_model']))
        
    ## Create agent graph
   # conn, stats = gg.create_graph_type(agents, properties) #This is where Kronecker should
    conn, stats = kg.create_graph_kronecker(agents, properties)
    
    for agent1 in conn.nodes():
        agent1.connect_to(conn.neighbors(agent1))

    nodes_to_try = balanced_node_sample(stats)  #  top_nodes (stats)    
    #print "Nodes", nodes_to_try

    for current_agent in nodes_to_try:
        #print "New node", current_agent
        if current_agent != -1:
            agents[current_agent].capacity = 10 ##set one agent to high capacity
            node_stats = current_agent_stats (current_agent, stats)
            agent_to_track = current_agent
        else:
            node_stats = {}
            agent_to_track = 0

        ## Distribute facts to agents
        for i in facts:
            for j in xrange(properties['agent_per_fact']):
                ## find a random agent, and distribute fact i
                k = random.randint(0,properties['num_agents']-1)
                agents[k].knowledge.add(i)
                
        ## Initialize agents to send everything that they think is valuable 
        ## in their outbox
        for agent in agents:
            agent.init_outbox()

        #action_list = []
        all_stats = ss.SimpleSimulationStats(properties['num_facts'],\
                                             properties['num_noise'],\
                                             stats['num_cc'],\
                                             properties['sa_increment'],\
                                             agent_to_track) #stats['largest_cc'], \
    
        ##actual simulation starts here
        for i in xrange(properties['num_steps']):
            x = one_step_simulation(agents)
            #action_list.append(x)
            if i%properties['statistic_taking_frequency'] == 0:
                all_stats.update_stats(agents,i)
    
        summary_results = all_stats.process_sa()
        
        density = stats['dens']
        
        results = {}
        results['setup'] = properties
        results['graph_type'] = properties['graph_type']

        results['total_filtered'] = summary_results['total_filtered']
        results['num_cc'] = summary_results['num_cc']
        results['size_lcc'] = summary_results['size_lcc']
        results['summary_results'] = summary_results
        results['all_sa'] = all_stats.sa
        results['all_comm'] = all_stats.comm
        results['all_sa0'] = all_stats.sa0
        results['all_comm0'] = all_stats.comm0
        results['steps'] = all_stats.steps
        results['node_stats'] = node_stats
        results['dens'] = density

        add_to_output(all_results, results, outfile)
        
        for agent in agents:
            agent.clear()
            agent.capacity = 1
    flush_results(all_results, outfile)

def run_simulation(properties, outfile):
    for i in xrange( properties['num_trial'] ):
        start = time.time()
        run_simulation_one_graph(properties, outfile)
        end = time.time()
        print "Trial: %d: simulation took %d seconds" %(i, end-start)


########## Main body

if __name__ == '__main__':

    #Make sure num_agents is equal to the final size of the kronecker (seednodes^interations)
    #init_edges is a list of where edges should be placed in seed matrix
    properties = {'connection_probability': 0.5, \
                  'num_nodes_to_attach': 5, \
                  'graph_type':'kronecker',\
                  'num_agents': int(math.pow(2, 5)), \
                  'agent_per_fact':1,\
                  'num_steps':10000,\
                  'num_trial':100,\
                  'statistic_taking_frequency': 1000, \
                  'num_facts':5000,\
                  'num_noise':0,\
                  'sa_increment': 500, \
                  'trust_used':False,\
                  'trust_filter_on':False,\
                  'inbox_trust_used':False,\
                  'agent_setup':[],\
                  'competence':1,\
                  'willingness':1,\
                  'spamminess':0,\
                  'selfishness':0,\
                  'twitter_model':True,\
                  'init_edges':[[1,0]],\
                  'alpha': 0.2,\
                  'beta': 0.09,\
                  'kron_interations':5,\
                  'kron_seed_nodes':2,\
                  'kron_seed_self_loops_stochastic':True} #added some kron specfic properties

    if len(sys.argv) > 1:
        outfile = sys.argv[1]
    else:
        outfile = "kronecker_results.txt"
    print "Writing results to", outfile

    f = open(outfile,"a")
    f.write( sj.dumps(properties) + "\n")
    f.close()
    
    run_simulation(properties, outfile)
        
