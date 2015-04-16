## good test cases for engagement versus decisiveness
## when there is a lot of noise, actually high engagement reduces the network performance 
## by multiplying the noise in the network instead of network filtering out noise slowly
## in problem cases with high con noise, other cases or when competence is high, engagement
## is good
## decisiveness plays a role too:  when decisiveness is 0.8, there is less penalty for
## high engagement as individuals have enough time to process information in the network
## at least I think so

import Cognitivesimulation as sim
import json 
import sys
import time
import simplejson as sj

num_fpro = 50
num_fcon = 40
num_groups = 1
num_agents = 31
agent_per_fact = 3
num_steps = 100
w = 1
c = 0.7
cap = 100
num_trials = 100
#graph_type = "spatial_random"
graph_type = "hierarchical"
radius = 0.2
agent_setup = []
spam = 0
selfish = 0
trust_used = False
inbox_trust_sorted = False
trust_filter_on  = False
e = 0.8
decisiveness = 0.8
corroboration_threshold = 1
fname = 'hier.txt'
cm = 0
disp = 0

params = {'competence' : [0.5,0.7,0.9],
#          'engagement' : [0.2,0.5,0.8],
#          'decisiveness' : [0.7, 0.8, 0.9],
#          'closedmindedness' : [0.0,0.5,1.0],
#          'corroboration_threshold' : [1,2,3], 
         }
         
if len(sys.argv) > 1:
    fname = sys.argv[1]

f = open(fname,"a")

for param in params.keys():
   for value in params[param]:
      for layer in range(5):
        change_list = [value]
        change_list.append(range(pow(2,layer)-1,pow(2,layer+1)-1))
        agent_setup = [{param : change_list}]
        for (num_npro, num_ncon) in [ (150,0), (125,25),(100,50),  (75,75), (50,100), (25,125), (0,150)  ]:
                results = sim.run_simulation(num_fpro, \
                                             num_fcon, \
                                             num_npro,\
                                             num_ncon, \
                                             num_groups, \
                                             num_agents, \
                                             agent_per_fact,\
                                             radius, \
                                             num_steps, \
                                             w, c, e, decisiveness, cm, \
                                             corroboration_threshold, \
                                             disp, \
                                             cap, \
                                             num_trials, \
                                             graph_type,\
                                             agent_setup,\
                                             spam, selfish,\
                                             trust_used,\
                                             inbox_trust_sorted, \
                                             trust_filter_on)

                f.write(sj.dumps(results) + "\n")

                

                infostr = "comp: %.2f, e: %.2f, good: %d/%d, bad: %d/%d, "\
                          "maxsa: %.2f, decisiveness: %.2f, agf: %d, cf: %d, capacity: %d" \
                          %(c, e, num_fpro, num_npro, num_fcon, num_ncon, \
                            results['all_sa'][-1][0]/90.,\
                            decisiveness, agent_per_fact, corroboration_threshold, cap)
                print infostr
                infostr = "correct/all: "
                for i in range(0,len(results['decisions'])):
                    if results['decisions'][i] == 0:
                        continue
                    infostr += " %d%%/%d "\
                        %(100*results['correct_decisions'][i]/(float(results['decisions'][i])), \
                          results['decisions'][i])
                    if results['decisions'][i] == 20 or \
                       (i > 0 and results['decisions'][i-1] == results['decisions'][i]):
                        break
                print infostr

