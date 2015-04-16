
import random 
import CognitiveAgent as Agent
import CognitiveGraphGen as gg
import CognitiveSimulationStats as SimulationStats
import networkx as nx
from simutil import * 


########## Initialization code

def create_connectivity(agents, p, type='undirected_random'):
    properties = {'graph_type' : type, 'connection_probability' : p}
    conn = gg.create_graph_type(agents, properties)[0]
        
    for agent1 in conn.nodes():
        agent1.connect_to(conn.neighbors(agent1))
    
    if type in ['hierarchy', 'collaborative']:
        return (1, len(agents))
    else:
        cc_conn = nx.connected_components(conn)
        ## return the number of connected components and 
        ## the size of the largest connected component
        return (len(cc_conn), len(cc_conn[0]))

def change_agent_property(agents, setup):
    """
    Setup is a dictionary that has new values and a ratio.
    It changes a proportion of agents given by the ratio to the 
    given values for the given properties.

    """
    who = range(len(agents))
    random.shuffle(who)
    ratio = setup['ratio']

    if ratio > 1 or ratio < -1:
        return ## error ratio, should return without changing anything

    cutoff = int(len(agents)*ratio)
    if 'competence' in setup.keys():
        for i in xrange(cutoff):
            agents[who[i]].competence = setup['competence']
    if 'engagement' in setup.keys():
        for i in xrange(cutoff):
            agents[who[i]].engagement = setup['engagement']
    if 'willingness' in setup.keys():
        for i in xrange(cutoff):
            agents[who[i]].willingness = setup['willingness']
    if 'spammer' in setup.keys():
        for i in xrange(cutoff):
            agents[who[i]].spammer = setup['spammer']
    if 'selfish' in setup.keys():
        for i in xrange(cutoff):
            agents[who[i]].selfish = setup['selfish']
            
def change_agent_property_strict(agents, setup):
    """
    Setup is a dictionary with a parameter as a key,
    and the value is an array containing two items,
    the new value for the parameter and a list of agents to update
    """
    
    if 'competence' in setup.keys():
       for i in setup['competence'][1]:
          agents[i].competence = setup['competence'][0]
    if 'engagement' in setup.keys():
       for i in setup['engagement'][1]:
          agents[i].engagement = setup['engagement'][0]
    if 'decisiveness' in setup.keys():
       for i in setup['decisiveness'][1]:
          agents[i].decisiveness = setup['decisiveness'][0]
    if 'closedmindedness' in setup.keys():
       for i in setup['closedmindedness'][1]:
          agents[i].closedmindedness = setup['closedmindedness'][0]
    if 'corroboration_threshold' in setup.keys():
       for i in setup['corroboration_threshold'][1]:
          agents[i].corroboration_threshold = setup['corroboration_threshold'][0]
    
   


########## Run simulation

def one_step_simulation(agents):
    num_actions = 0
    all_actions = []
    for agent in agents:
        actions_taken = agent.act()  ##list of (n, fact)
        all_actions.extend(actions_taken)

    random.shuffle(all_actions)
    for (n,fact) in all_actions:
        num_actions += 1
        n.receive(fact, agent)
    return num_actions


def multi_step_simulation(NUM_FPRO, NUM_FCON, NUM_NPRO, NUM_NCON, NUM_GROUPS, \
                          NUM_AGENTS, AGENT_PER_FACT, CONNECTION_PROBABILITY, \
                          NUM_STEPS, WILLINGNESS, COMPETENCE, DISP, CAPACITY, \
                          ENGAGEMENT, DECISIVENESS, CM, \
                          CORROBORATION_THRESHOLD,  \
                          GRAPH_TYPE, AGENT_SETUP=[], \
                          SPAMMINESS=0, SELFISHNESS=0, \
                          TRUST_USED=True, INBOX_TRUST_SORTED=False, \
                          TRUST_FILTER_ON=True):
    
    facts = range((NUM_FPRO + NUM_FCON + NUM_NPRO + NUM_NCON)*NUM_GROUPS)
    random.shuffle(facts)
    ##print "Created", len(facts), "facts"

    agents = []
    for i in xrange(NUM_AGENTS):
        agents.append ( Agent.Agent(WILLINGNESS, COMPETENCE, \
                                    ENGAGEMENT, DECISIVENESS, CM, \
                                    CORROBORATION_THRESHOLD, \
                                    DISP, CAPACITY, \
                                    NUM_FPRO, NUM_FCON,\
                                    NUM_NPRO, NUM_NCON, \
                                    NUM_GROUPS, \
                                    SPAMMINESS, SELFISHNESS, \
                                    TRUST_USED, INBOX_TRUST_SORTED, \
                                    TRUST_FILTER_ON) )

    ## Now, change the properties of some agents 
    ## based on the agent setup data
    for setup in AGENT_SETUP: ## each setup is a dictionary
        change_agent_property_strict(agents, setup)

    ##print "Created" , len(agents), "agents"

    ## Create agent graph
    (num_cc, size_lcc) = create_connectivity(agents, CONNECTION_PROBABILITY, GRAPH_TYPE)

    ## Distribute facts to agents
    for i in facts:
        for j in xrange(AGENT_PER_FACT):
            ## find a random agent, and distribute fact i
            k = random.randint(0,NUM_AGENTS-1)
            agents[k].receive(i, None )
            #agents[k].add_fact(i, i % (NUM_FPRO + NUM_FCON + NUM_NPRO + NUM_NCON) < (NUM_FPRO + NUM_FCON))
            
    ## Initialize agents to send everything that they think is valuable 
    ## in their outbox
    ##for agent in agents:
    ##    agent.init_outbox()

    action_list = []
    all_stats = SimulationStats.SimulationStats((NUM_FPRO + NUM_FCON) * NUM_GROUPS, \
                                                (NUM_NPRO + NUM_NCON) * NUM_GROUPS, \
                                                num_cc, \
                                                size_lcc)
    for i in xrange(NUM_STEPS):
        x = one_step_simulation(agents)
        action_list.append(x)
        if i%5 == 0:
            all_stats.update_stats(agents,i)


    return all_stats


def run_simulation(NUM_FPRO, NUM_FCON, NUM_NPRO, NUM_NCON, NUM_GROUPS, \
                   NUM_AGENTS, AGENT_PER_FACT, CONNECTION_PROBABILITY, \
                   NUM_STEPS,  WILLINGNESS, COMPETENCE, \
                   ENGAGEMENT, DECISIVENESS, CM,\
                   CORROBORATION_THRESHOLD, \
                   DISP, CAPACITY,\
                   NUM_TRIAL, GRAPH_TYPE, AGENT_SETUP=[], \
                   SPAMMINESS=0, SELFISHNESS=0, \
                   TRUST_USED=True, INBOX_TRUST_SORTED = False,\
                   TRUST_FILTER_ON=True):
    all_stats = multi_step_simulation(NUM_FPRO, \
                                      NUM_FCON, \
                                      NUM_NPRO, \
                                      NUM_NCON, \
                                      NUM_GROUPS, \
                                      NUM_AGENTS, \
                                      AGENT_PER_FACT,\
                                      CONNECTION_PROBABILITY,\
                                      NUM_STEPS, WILLINGNESS,\
                                      COMPETENCE, DISP, CAPACITY, ENGAGEMENT, \
                                      DECISIVENESS, CM, \
                                      CORROBORATION_THRESHOLD, \
                                      GRAPH_TYPE,\
                                      AGENT_SETUP, \
                                      SPAMMINESS, SELFISHNESS, \
                                      TRUST_USED, \
                                      INBOX_TRUST_SORTED, \
                                      TRUST_FILTER_ON )

    for i in xrange(1, NUM_TRIAL):
        new_stats = multi_step_simulation(NUM_FPRO, NUM_FCON, \
                                          NUM_NPRO, NUM_NCON, \
                                          NUM_GROUPS, NUM_AGENTS, \
                                          AGENT_PER_FACT, \
                                          CONNECTION_PROBABILITY,\
                                          NUM_STEPS, WILLINGNESS,\
                                          COMPETENCE, DISP, CAPACITY, ENGAGEMENT, \
                                          DECISIVENESS, CM,\
                                          CORROBORATION_THRESHOLD, \
                                          GRAPH_TYPE, \
                                          AGENT_SETUP, \
                                          SPAMMINESS, SELFISHNESS, \
                                          TRUST_USED, \
                                          INBOX_TRUST_SORTED, \
                                          TRUST_FILTER_ON )
        all_stats.merge_stats(new_stats)

    summary_results = all_stats.process_sa()

    results = {}
    results['setup'] = {'num_pro_facts':NUM_FPRO, \
                        'num_con_facts':NUM_FCON, \
                        'num_pro_noise':NUM_NPRO, \
                        'num_con_noise':NUM_NCON,\
                        'num_groups':NUM_GROUPS,\
                        'num_agents':NUM_AGENTS, \
                        'agent_per_fact':AGENT_PER_FACT, \
                        'connection_probability_or_radius': CONNECTION_PROBABILITY, \
                        'num_steps': NUM_STEPS,\
                        'willingness': WILLINGNESS,\
                        'competence': COMPETENCE,\
                        'engagement': ENGAGEMENT,\
                        'decisiveness': DECISIVENESS,\
                        'closedmindedness': CM,\
                        'corroboration_threshold': CORROBORATION_THRESHOLD,\
                        'predisposition': DISP,\
                        'capacity': CAPACITY,\
                        'spamminess': SPAMMINESS, \
                        'selfishness': SELFISHNESS, \
                        'trust_used': TRUST_USED,\
                        'inbox_trust_sorted': INBOX_TRUST_SORTED, \
                        'trust_filter_on': TRUST_FILTER_ON, \
                        'num_trial': NUM_TRIAL,\
                        'graph_type': GRAPH_TYPE,\
                        'agent_setup': AGENT_SETUP}
    results['total_filtered'] = summary_results['total_filtered']
    results['num_cc'] = summary_results['num_cc']
    results['size_lcc'] = summary_results['size_lcc']
    results['summary_results'] = summary_results
    results['all_sa'] = all_stats.sa
    results['all_comm'] = all_stats.comm
    results['all_sa0'] = all_stats.sa0
    results['all_comm0'] = all_stats.comm0
    results['steps'] = all_stats.steps
    results['decisions'] = all_stats.decisions
    results['correct_decisions'] = all_stats.correct_decisions

    return (results)
    
########## Main body

if __name__ == '__main__':

    random.seed(10)

    NUM_FACTS = 50
    NUM_NOISE = 500
    NUM_AGENTS = 20
    AGENT_PER_FACT = 1
    CONNECTION_PROBABILITY = 0.5
    NUM_STEPS = 10000 ## how many steps to run each simulation
    WILLINGNESS = 1
    COMPETENCE = 1
    GRAPH_TYPE = 'spatial_random'

    NUM_TRIAL = 1
    ## number of times to repeat the simulation for averaging out values 

    # for i in xrange(5):
    #     w = 0.2 + 0.2*i
    #     for j in xrange(5):
    #         c = 0.2 + 0.2*j
    for i in xrange(2):
        w = 0.5 + 0.5*i
        for j in xrange(2):
            c = 0.5 + 0.5*j
            e = u = 1
            results = run_simulation(NUM_FACTS, \
                                     NUM_NOISE, NUM_AGENTS, \
                                     AGENT_PER_FACT,\
                                     CONNECTION_PROBABILITY, \
                                     NUM_STEPS, w, c, e, u, \
                                     4, \
                                     NUM_TRIAL, \
                                     GRAPH_TYPE, \
                                     AGENT_SETUP=[{ "ratio" : 0.2,\
                                                    "spammer" : 0.8, \
                                                    "competence":0.2 }])
            
            ##print results
            print 'w, c, num_cc, size_lcc'
            print w, c, results['num_cc'], results['size_lcc']
            print results
