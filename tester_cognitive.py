import Cognitivesimulation as sim
import json 
import sys
import time

num_fpro = 50
num_fcon = 40
num_npro = 40
num_ncon = 40
num_groups = 1
num_agents = 20
agent_per_fact = 1
radius = 0.5
num_steps = 100
w = 1
c = 0.8
e = 0.6
u = 50
cap = 20
num_trials = 400
graph_type = "spatial_random"
agent_setup = []
spam = 0
selfish = 0
trust_used = False
inbox_trust_sorted = False
trust_filter_on  = False


for i in range(1,6):
    e = 0.2*i
    results = sim.run_simulation(num_fpro, \
                                 num_fcon, \
                                 num_npro,\
                                 num_ncon, \
                                 num_groups, \
                                 num_agents, \
                                 agent_per_fact,\
                                 radius, \
                                 num_steps, \
                                 w, c, e, u, \
                                 cap, \
                                 num_trials, \
                                 graph_type,\
                                 agent_setup,\
                                 spam, selfish,\
                                 trust_used,\
                                 inbox_trust_sorted, \
                                 trust_filter_on)
    
    # for val in results['summary_results']['sa_at_value']:
    #     print "%d%% (%.2f/%.2f), sa: %.2f, comm: %d, steps: %d" \
    #         %(100*val['correct_decisions']/float(1+val['decisions']), \
    #           val['correct_decisions'], \
    #           val['decisions'], \
    #           val['sa'], \
    #           val['comm'],\
    #           val['steps'])

    #print results.keys()

    count = 0
    for i in range(0,100):
        if results['decisions'][i] == 0:
            continue
        count += 1
        print "comp: %.2f, e: %.2f, correct: %d %%, decisions: %d, sa: %d, comm: %d, steps: %d" \
            %(c, e,\
              100*results['correct_decisions'][i]/(float(results['decisions'][i])), \
              results['correct_decisions'][i], \
              results['all_sa'][i][0], \
              results['all_comm'][i], \
              results['steps'][i])
        if count > 3:
            break

##decisions, correct_decisions, decisions, comm, steps, sa
## summary_decisions/sa_at_value: {steps/sa/comm/decisions/correct_decisions}
