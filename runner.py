"""
    The runner requires an input configuration file 
    --see template for an example, and an output file for the results.
    Example:   python runner.py config_file output_file
"""

import simulation as sim
import simplejson as sj
import random
import sys

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print "Usage: python runner.py config_file output_file"
        sys.exit()

    config_file = sys.argv[1]
    output_file = sys.argv[2]

    random.seed(10)

    ## Read input configuration
    f = open(config_file)
    config = sj.loads(f.read())
    f.close()

    ## Set output configuration
    f = open(output_file,"w")
    f.write (sj.dumps(config))
    f.write ('\n')
    f.close()

    num_steps = config['num_steps']
    num_trials = config['num_trials']
    trust_used = config['trust_used']
    inbox_trust_sorted = config['inbox_trust_sorted']
    if 'trust_filter_on' in config.keys():
        trust_filter_on = config['trust_filter_on']
    else:
        trust_filter_on = True

    i = 1

    for num_fact in config['num_facts']:
        for num_noise in config['num_noise']:
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
    
                                            print "Case", i, "being executed"
                                            print "running for %d/%d facts %d agents"\
                                                %(num_fact, num_noise, num_agents)
                                            print "\t%d facts per agent "\
                                                %agent_per_fact
                                            print "\t%s/%.1f graph for %s steps" \
                                                %(graph_type, radius, num_steps)
                                            print "\tw:%.1f/c:%.1f for %d trials"\
                                                %(w,c,num_trials)
                                            print "\tagent setup", agent_setup
                                            i += 1
        
                                            results = sim.run_simulation(num_fact, \
                                                                         num_noise,\
                                                                         num_agents, \
                                                                         agent_per_fact,\
                                                                         radius, \
                                                                         num_steps, \
                                                                         w, c, \
                                                                         num_trials, \
                                                                         graph_type,\
                                                                         agent_setup,\
                                                                         spam, selfish,\
                                                                         trust_used,\
                                                                         inbox_trust_sorted, \
                                                                         trust_filter_on)
                                    
                                    f = open(output_file,"a")
                                    f.write( sj.dumps(results) )
                                    f.write("\n")
                                    f.close()

