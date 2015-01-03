"""
    The runner requires an input configuration file 
    --see template for an example, and an output file for the results.
    Example:   python runner.py config_file output_file
"""

import Cognitivesimulation as sim
import simplejson as sj
import socket
import random
import sys

def output(output_loc, is_slave, identity, text):
    if is_slave:
        sock = socket.socket()
        sock.connect((output_loc,2436))
        sock.sendall(identity)
        sock.sendall("output..")
        sock.sendall('{0:0>8}'.format(str(len(text))))
        sock.sendall(text)
        sock.close()
        
    else:
        f = open(output_loc,"a")
        f.write (text)
        f.close

def run(config_file, output_loc, is_slave, identity):
    random.seed(10)

    ## Read input configuration
    f = open(config_file)
    config = sj.loads(f.read())
    f.close()

    ## Set output configuration
    output(output_loc, is_slave, identity, sj.dumps(config) + '\n')

    num_steps = config['num_steps']
    num_trials = config['num_trials']
    trust_used = config['trust_used']
    inbox_trust_sorted = config['inbox_trust_sorted']
    if 'trust_filter_on' in config.keys():
        trust_filter_on = config['trust_filter_on']
    else:
        trust_filter_on = True

    i = 1

    for num_fpro in config['num_fpro']:
       for num_fcon in config['num_fcon']:
           for num_npro in config['num_npro']:
              for num_ncon in config['num_ncon']:
                  for num_groups in config['num_groups']:
                     for num_agents in config['num_agents']:
                         for agent_per_fact in config['agent_per_fact']:
                             for graph in config['graph_description']:
                                 graph_type = graph['type']
                                 radius = graph['radius']
                                 for agent_setup in config['agent_setup']:
                                     for w in config['willingness']:
                                         for c in config['competence']:
                                             for spam in config['spamminess']:
                                                 for selfish in config['selfishness']:
                                                    for e in config['engagement']:
                                                       for u in config ['uncertainty_handling']:
                                                           for cap in config ['capacity']:
             
                                                              print "Case", i, "being executed"
                                                              print "running for %d/%d facts per group %d groups %d agents"\
                                                                  %(num_fpro+num_fcon, num_npro+num_ncon, num_groups, num_agents)
                                                              print "\t%d agents per fact "\
                                                                  %agent_per_fact
                                                              print "\t%s/%.1f graph for %s steps" \
                                                                  %(graph_type, radius, num_steps)
                                                              print "\tw:%.1f/c:%.1f/e:%.1f/u:%.1f for %d trials"\
                                                                  %(w,c,e,u,num_trials)
                                                              print "\tagent setup", agent_setup
                                                              i += 1
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
                                                              output(output_loc, is_slave, identity, sj.dumps(results) + '\n' )

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print "Usage: python runner.py config_file output_file"
        sys.exit()

    config_file = sys.argv[1]
    output_file = sys.argv[2]
    run(config_file, output_file, False, 0)
