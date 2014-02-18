
import random 
import Agent 
import GraphGen as gg
import networkx as nx
from simutil import * 

EPSILON = 0.05


def num_good_facts(agent, NUM_FACTS):
    x = list( agent.knowledge )
    x.sort()
    last_fact = -1
    for i in x:
        if i >= NUM_FACTS:
            last_fact = i
            break
    if last_fact == -1:
        return len(x)
    else:
        return x.index(last_fact)-1


def find_sa(agents, NUM_FACTS):
    sa = []
    for agent in agents:
        sa.append ( num_good_facts(agent, NUM_FACTS) )
    return (max(sa), meanstd(sa))

## need to add max sa, comm/time to max sa

def process_sa(sa, all_comm, NUM_FACTS):
    NUM_FACTS = float(NUM_FACTS)
    ## find the highest sa value first
    highest_index = len(sa)-1  #avg sa
    highest_value = sa[-1][0]

    max_highest_index = len(sa)-1 # max sa
    max_highest_value = sa[-1][2]

    for i in xrange(len(sa)-2,1,-1):
        if sa[i+1][0] - sa[i][0] <= EPSILON:
            highest_index = i
            highest_value = sa[i][0]
        if sa[i+1][2] - sa[i][2] <= EPSILON:
            max_highest_index = i
            max_highest_value = sa[i][2]
    sa_at_value = []    ## store comm and steps values for a specific sa 
    next_sa_to_search = 10
    for i in xrange(len(sa)):
        if sa[i][0] >= next_sa_to_search:
            sa_at_value.append (
                {'sa': next_sa_to_search/NUM_FACTS,\
                 'comm': all_comm[i],\
                 'steps': i*100})
            next_sa_to_search += 10

    summary = { 'steps': highest_index*100, \
                'sa': highest_value/NUM_FACTS, \
                'comm': all_comm[highest_index], \
                'steps_maxsa': max_highest_index*100, \
                'maxsa': max_highest_value/NUM_FACTS, \
                'comm_maxsa': all_comm[max_highest_index], \
                'sa_at_value': sa_at_value }
    return summary

########## Initialization code

def create_connectivity(agents, p, type='undirected_random'):
    if type == 'directed_random':
        conn = gg.random_undirected_graph(agents, p)
    elif type == 'spatial_random':
        conn = gg.spatial_random_graph(agents, p)
    else:
        conn = gg.random_directed_graph(agents, p)
        
    for agent1 in conn.nodes():
        agent1.connect_to(conn.neighbors(agent1))
    
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
    if 'willingness' in setup.keys():
        for i in xrange(cutoff):
            agents[who[i]].willingness = setup['willingness']
    if 'spammer' in setup.keys():
        for i in xrange(cutoff):
            agents[who[i]].spammer = setup['spammer']
    if 'selfish' in setup.keys():
        for i in xrange(cutoff):
            agents[who[i]].selfish = setup['selfish']


########## Print statistics

def agent_stats(agents):
    fact_dist = []
    neighbor_dist = []
    for agent in agents:
        (f,n) = agent.stat()
        fact_dist.append (f)
        neighbor_dist.append (n)
    print "Facts per agent", (1.0*sum(fact_dist))/len(fact_dist)
    print "Neighbors per agent", (1.0*sum(neighbor_dist))/len(neighbor_dist)


def full_comms(agents):
    val = 0
    filtered = 0
    for agent in agents:
        val += agent.numsent
        filtered += agent.num_filtered
    return (val, filtered)

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


def multi_step_simulation(NUM_FACTS, NUM_NOISE, NUM_AGENTS, \
                          AGENT_PER_FACT, CONNECTION_PROBABILITY, \
                          NUM_STEPS, WILLINGNESS, COMPETENCE, \
                          GRAPH_TYPE, AGENT_SETUP=[], \
                          SPAMMINESS=0, SELFISHNESS=0, \
                          TRUST_USED=True, INBOX_TRUST_SORTED=False, \
                          TRUST_FILTER_ON=True):
    
    facts = range(NUM_FACTS + NUM_NOISE)
    ##print "Created", len(facts), "facts"

    agents = []
    for i in xrange(NUM_AGENTS):
        agents.append ( Agent.Agent(WILLINGNESS, COMPETENCE, \
                                    NUM_FACTS, NUM_NOISE,\
                                    SPAMMINESS, SELFISHNESS, \
                                    TRUST_USED, INBOX_TRUST_SORTED, \
                                    TRUST_FILTER_ON) )

    ## Now, change the properties of some agents 
    ## based on the agent setup data
    for setup in AGENT_SETUP: ## each setup is a dictionary
        change_agent_property(agents, setup)

    ##print "Created" , len(agents), "agents"

    ## Create agent graph
    (num_cc, size_lcc) = create_connectivity(agents, CONNECTION_PROBABILITY, GRAPH_TYPE)

    ## Distribute facts to agents
    for i in facts:
        for j in xrange(AGENT_PER_FACT):
            ## find a random agent, and distribute fact i
            k = random.randint(0,NUM_AGENTS-1)
            agents[k].add_fact(i)
            
    #agent_stats(agents)

    ## Initialize agents to send everything that they think is valuable 
    ## in their outbox
    for agent in agents:
        agent.init_outbox()

    action_list = []
    sa = []
    comm = []
    diagnostics_on = False
    total_num_filtered = 0
    for i in xrange(NUM_STEPS):
        x = one_step_simulation(agents)
        action_list.append(x)
        if i%100 == 0:
            (maxsa, (m,s)) = find_sa(agents, NUM_FACTS)
            ##if len(sa) != 0 and ((m-sa[-1][0]) < EPSILON):
            ##    break
            sa.append( [m,s, maxsa] )
            (c,f) = full_comms(agents)
            comm.append(c)
            total_num_filtered += f

            if diagnostics_on:
                f = open("trust_data.txt","a")
                f.write("***** %.1f/%.1f *******\n" %(WILLINGNESS, COMPETENCE))
                for a in agents: 
                    f.write(a.get_trust_for_neighbors()+"\n")
                f.close()

    return (sa, comm, num_cc, size_lcc, total_num_filtered)


def run_simulation(NUM_FACTS, NUM_NOISE, NUM_AGENTS, \
                   AGENT_PER_FACT, CONNECTION_PROBABILITY, \
                   NUM_STEPS,  WILLINGNESS, COMPETENCE, NUM_TRIAL,\
                   GRAPH_TYPE, AGENT_SETUP=[], \
                   SPAMMINESS=0, SELFISHNESS=0, \
                   TRUST_USED=True, INBOX_TRUST_SORTED = False,\
                   TRUST_FILTER_ON=True):
    all_num_cc = 0.0
    all_size_lcc = 0.0
    total_filtered = 0.0
    (all_sa, all_comm, \
     num_cc, size_lcc, f) = multi_step_simulation(NUM_FACTS,\
                                                  NUM_NOISE, \
                                                  NUM_AGENTS, \
                                                  AGENT_PER_FACT,\
                                                  CONNECTION_PROBABILITY,\
                                                  NUM_STEPS, WILLINGNESS,\
                                                  COMPETENCE, GRAPH_TYPE,\
                                                  AGENT_SETUP, \
                                                  SPAMMINESS, SELFISHNESS, \
                                                  TRUST_USED, \
                                                  INBOX_TRUST_SORTED, \
                                                  TRUST_FILTER_ON )
    all_num_cc += num_cc
    all_size_lcc += size_lcc
    total_filtered += f

    for i in xrange(1, NUM_TRIAL):
        (sa, comm, \
         num_cc, size_lcc, f) = multi_step_simulation(NUM_FACTS, NUM_NOISE, \
                                                      NUM_AGENTS, \
                                                      AGENT_PER_FACT, \
                                                      CONNECTION_PROBABILITY,\
                                                      NUM_STEPS, WILLINGNESS,\
                                                      COMPETENCE, GRAPH_TYPE, \
                                                      AGENT_SETUP, \
                                                      SPAMMINESS, SELFISHNESS, \
                                                      TRUST_USED, \
                                                      INBOX_TRUST_SORTED, \
                                                      TRUST_FILTER_ON )
        all_num_cc += num_cc
        all_size_lcc += size_lcc
        total_filtered += f
        for j in xrange(len(sa)):
            all_comm[j] += comm[j]
            all_sa[j][0] += sa[j][0]
            all_sa[j][1] += sa[j][1]
            all_sa[j][2] += sa[j][2]


    for j in xrange(len(all_sa)):
        all_sa[j][0] = all_sa[j][0]*1.0/NUM_TRIAL
        all_sa[j][1] = all_sa[j][1]*1.0/NUM_TRIAL
        all_sa[j][2] = all_sa[j][2]*1.0/NUM_TRIAL
        all_comm[j] = all_comm[j]*1.0/NUM_TRIAL

    total_filtered /= NUM_TRIAL
    summary_results = process_sa(all_sa, all_comm, NUM_FACTS)

    results = {}
    results['setup'] = {'num_facts':NUM_FACTS, \
                        'num_noise': NUM_NOISE,\
                        'num_agents':NUM_AGENTS, \
                        'agent_per_fact':AGENT_PER_FACT, \
                        'connection_probability_or_radius': CONNECTION_PROBABILITY, \
                        'num_steps': NUM_STEPS,\
                        'willingness': WILLINGNESS,\
                        'competence': COMPETENCE,\
                        'spamminess': SPAMMINESS, \
                        'selfishness': SELFISHNESS, \
                        'trust_used': TRUST_USED,\
                        'inbox_trust_sorted': INBOX_TRUST_SORTED, \
                        'trust_filter_on': TRUST_FILTER_ON, \
                        'num_trial': NUM_TRIAL,\
                        'graph_type': GRAPH_TYPE,\
                        'agent_setup': AGENT_SETUP}
    results['total_filtered'] = total_filtered
    results['num_cc'] = all_num_cc/NUM_TRIAL
    results['size_lcc'] = all_size_lcc/NUM_TRIAL
    results['summary_results'] = summary_results
    results['all_sa'] = all_sa
    results['all_comm'] = all_comm

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
            results = run_simulation(NUM_FACTS, \
                                         NUM_NOISE, NUM_AGENTS, \
                                         AGENT_PER_FACT,\
                                         CONNECTION_PROBABILITY, \
                                         NUM_STEPS, w, c, NUM_TRIAL, \
                                         GRAPH_TYPE, \
                                         AGENT_SETUP=[{ "ratio" : 0.2,\
                                                            "spammer" : 0.8, \
                                                            "competence":0.2 }])
            
            ##print results
            print 'w, c, num_cc, size_lcc'
            print w, c, results['num_cc'], results['size_lcc']
            print results
