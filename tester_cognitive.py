import Cognitivesimulation as sim
import json 
import sys
import time

num_fpro = 50
num_fcon = 20
num_npro = 100
num_ncon = 130
num_groups = 1
num_agents = 20
agent_per_fact = 1
radius = 0.5
num_steps = 10000
w = 1
c = 0.6
e = 0.6
u = 10
cap = 10
num_trials = 10
graph_type = "spatial_random"
agent_setup = []
spam = 0
selfish = 0
trust_used = False
inbox_trust_sorted = False
trust_filter_on  = False

start = time.time()
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

end = time.time()

for val in results['summary_results']['sa_at_value']:
    print "%d%% (%.2f/%.2f), sa: %.2f, comm: %d, steps: %d" \
        %(100*val['correct_decisions']/float(1+val['decisions']), \
          val['correct_decisions'], \
          val['decisions'], \
          val['sa'], \
          val['comm'],\
          val['steps'])

print "Time elapsed", end-start
