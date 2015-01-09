import Cognitivesimulation as sim
import json 
import sys
import time

num_fpro = 50
num_fcon = 40
num_npro = 100
num_ncon = 100
num_groups = 1
num_agents = 20
agent_per_fact = 2
radius = 0.5
num_steps = 120
w = 1
c = 0.4
e = 0.6
u = 10
corraboration_threshold = 4
cap = 10
num_trials = 10
graph_type = "spatial_random"
#graph_type = "newman_watts_strogatz_graph"
#radius = 0.1
agent_setup = []
spam = 0
selfish = 0
trust_used = False
inbox_trust_sorted = False
trust_filter_on  = False

fname = 'out.txt'

if len(sys.argv) > 1:
    fname = sys.argv[1]

#for u in [10,25]:
for u in [25]:
    #for (num_npro, num_ncon) in [ (100,100), (500,500), (100,500) ]:
    for (num_npro, num_ncon) in [ (100,200) ]:
        #for c in [0.4, 0.6, 0.8]:
        for c in [0.8]:
            #for e in [0.4, 0.8]:
            for e in [0.2, 0.4, 0.6, 0.8, 1]:
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
                                             corraboration_threshold, \
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
                

                fout = open(fname,"a")
                for i in range(0,len(results['decisions'])):
                    if results['decisions'][i] == 0:
                        continue
                    infostr = "comp: %.2f, e: %.2f, good: %d/%d, bad: %d/%d, "\
                        "correct: %d %%, decisions: %d, sa: %d, "\
                        "comm: %d, steps: %d, maxsa: %.2f, deadline: %d, agf: %d" \
                        %(c, e, num_fpro, num_npro, num_fcon, num_ncon, \
                          100*results['correct_decisions'][i]/(float(results['decisions'][i])), \
                          results['decisions'][i], \
                          results['all_sa'][i][0]/90., \
                          results['all_comm'][i], \
                          results['steps'][i], \
                          results['all_sa'][-1][0]/90.,\
                          u, agent_per_fact)
                    print infostr
                    #fout.write( infostr + "\n")
                    if results['decisions'][i] == 20:
                        break
                fout.close()
                print

##decisions, correct_decisions, decisions, comm, steps, sa
## summary_decisions/sa_at_value: {steps/sa/comm/decisions/correct_decisions}
