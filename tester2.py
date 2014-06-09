
import random 
import Agent 
import GraphGen as gg
import SimulationStats as ss
import networkx as nx
from simutil import * 
import simplejson as sj

def current_agent_stats (current_agent, stats):
    node_stats = {}
    node_stats['cc'] = stats['cc'][current_agent]
    node_stats['bc'] = stats['bc'][current_agent]
    node_stats['deg'] = stats['deg'][current_agent]
    return node_stats

def top_nodes (stats): 
    """ Return top 100, or all if less than 100 nodes in decreasing order
    of closeness centrality.

    """

    best_list = []
    for key in stats['cc'].keys():
        best_list.append( (stats['cc'][key], key) )
    best_list.sort(reverse=True)
    nodes = []
    num_to_extract = min(50, len(best_list))
    for (val, node) in best_list[: num_to_extract]:
        nodes.append(node)
    return nodes

def add_to_output(results, outfile):
    f = open(outfile,"a")
    f.write( sj.dumps(results) + "\n")
    f.close()

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
    for i in xrange(properties['num_agents']):
        agents.append ( Agent.Agent(properties['willingness'],\
                                    properties['competence'],\
                                    properties['num_facts'],\
                                    properties['num_noise'],\
                                    properties['spamminess'],\
                                    properties['selfishness'],\
                                    properties['trust_used'],\
                                    properties['inbox_trust_used'],\
                                    properties['trust_filter_on']) )

    ## Create agent graph
    conn, stats = gg.create_graph_type(agents, properties)

    for agent1 in conn.nodes():
        agent1.connect_to(conn.neighbors(agent1))

    nodes_to_try = top_nodes (stats)        
    #print "Nodes", nodes_to_try

    for current_agent in nodes_to_try:
        #print "New node", current_agent
        agents[current_agent].capacity = 50 ##set one agent to high capacity
        node_stats = current_agent_stats (current_agent, stats)
    
        ## Distribute facts to agents
        for i in facts:
            for j in xrange(properties['agent_per_fact']):
                ## find a random agent, and distribute fact i
                k = random.randint(0,properties['num_agents']-1)
                agents[k].add_fact(i)
                
        ## Initialize agents to send everything that they think is valuable 
        ## in their outbox
        for agent in agents:
            agent.init_outbox()
    
        action_list = []
        all_stats = ss.SimulationStats(properties['num_facts'], \
                                       properties['num_noise'],\
                                       stats['num_cc'], stats['largest_cc'])
    
        ##actual simulation starts here
        for i in xrange(properties['num_steps']):
            x = one_step_simulation(agents)
            action_list.append(x)
            if i%100 == 0:
                all_stats.update_stats(agents,i)
    
        summary_results = all_stats.process_sa()
    
        results = {}
        results['setup'] = properties
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

        add_to_output(results, outfile)
        
        for agent in agents:
            agent.clear()
            agent.capacity = 1


def run_simulation(properties, outfile):
    for i in xrange( properties['num_trial'] ):
        run_simulation_one_graph(properties, outfile)
        if i%10==0:
            print "Iteration", i

########## Main body

if __name__ == '__main__':
    gtypes = ['random', 'watts_strogatz_graph', \
              'newman_watts_strogatz_graph', 'barabasi_albert_graph', \
              'powerlaw_cluster_graph', 'cycle_graph', 'star' ]
    gtypes = ['watts_strogatz_graph', \
              'barabasi_albert_graph', \
              'powerlaw_cluster_graph' ]
    random.seed(10)
    properties = {'connection_probability': 0.5, \
                  'num_nodes_to_attach': 5, \
                  'graph_type':'star',\
                  'num_agents': 20, \
                  'agent_per_fact':1,\
                  'num_steps':50000,\
                  'num_trial':50,\
                  'num_facts':50000,\
                  'num_noise':0,\
                  'trust_used':False,\
                  'trust_filter_on':False,\
                  'inbox_trust_used':False,\
                  'agent_setup':[],\
                  'competence':1,\
                  'willingness':1,\
                  'spamminess':0,\
                  'selfishness':0 }

    for numa in [20]:
        properties['num_agents'] = numa
        for g in gtypes:
            properties['graph_type'] = g
            print "starting with", g, "and", numa
            run_simulation(properties, "gtype_results_new.txt")
        
