""" Keeping track of statistics for agents

"""

from simutil import * 

class SimulationStats(object):

        def __init__ (self, NUM_FACTS, NUM_NOISE, num_cc=0, size_lcc=0, sa_increment=10):
            self.NUM_FACTS = float(NUM_FACTS)
            self.NUM_NOISE = NUM_NOISE
            self.sa = []  ## triples of the form mean, std, max sa of all agents
            self.sa0 = []  ## a single value, sa of agent at 0
            self.comm = [] ## list of total communication values 
                           ## over all agents for each at time step
            self.comm0 = [] ## list of communication values for agent at 0
            self.decisions = [] ##  number decisions made of all agents
            self.correct_decisions = [] ##  number correct decisions of all agents
            self.steps = [] ## steps at which all other stats are recorded.
            self.total_filtered = 0
            self.num_cc = num_cc
            self.size_lcc = size_lcc
            self.num_appended = 1.0 ## how many stats objects are combined
            self.EPSILON = 0.01
            self.sa_increment = sa_increment

        def __str__ (self):
            return (str(self.sa0) + "\n" + str(self.comm))

        def merge_stats( self, other ):
            for i in xrange(len(self.steps)):
                self.sa[i][0] += other.sa[i][0]
                self.sa[i][1] += other.sa[i][1]
                self.sa[i][2] += other.sa[i][2]
                self.sa0[i] += other.sa0[i]
                self.comm[i] += other.comm[i]
                self.comm0[i] += other.comm0[i]
                self.total_filtered += other.total_filtered
                self.num_cc += other.num_cc
                self.size_lcc += other.size_lcc
                self.decisions[i] += other.decisions[i]
                self.correct_decisions[i] += other.correct_decisions[i]
            self.num_appended += 1

        def normalize( self ):
            for i in xrange(len(self.steps)):
                self.sa[i][0] /= self.num_appended
                self.sa[i][1] /= self.num_appended
                self.sa[i][2] /= self.num_appended
                self.decisions[i] /= self.num_appended
                self.correct_decisions[i] /= self.num_appended
                self.sa0[i] /= self.num_appended
                self.comm[i] /= self.num_appended
                self.comm0[i] /= self.num_appended
            self.total_filtered /= self.num_appended
            self.num_cc /= self.num_appended
            self.size_lcc /= self.num_appended
            self.num_appended = 1.0

        def num_good_facts(self, agent):
            return len(agent.facts_known)
        
        def find_sa(self, agents):
            cur_sa = []
            for agent in agents:
                cur_sa.append ( self.num_good_facts(agent) )
            return (max(cur_sa), meanstd(cur_sa))
        
        def full_comms(self, agents):
            val = 0
            filtered = 0
            for agent in agents:
                val += agent.numsent
                filtered += agent.num_filtered
            return (val, filtered)
            
        def find_decisions(self, agents):
            decisions = 0
            correct_decisions = 0
            for agent in agents:
                if agent.decisions > 5:
                   print "foobar"
                decisions += agent.decisions
                correct_decisions += agent.correct_decisions
            return (decisions, correct_decisions)

        def update_stats(self, agents, steps):
            (maxsa, (m,s)) = self.find_sa(agents)
            self.sa0.append( self.num_good_facts(agents[0]) )
            self.sa.append ( [m,s, maxsa] )
            (d, c) = self.find_decisions(agents)
            self.decisions.append(d)
            self.correct_decisions.append(c)
            (c,f) = self.full_comms(agents)
            self.comm.append(c)
            self.comm0.append( agents[0].numsent )
            self.total_filtered += f
            self.steps.append(steps)

        def process_sa( self ):
            self.normalize()

            ## First AVG SA processing
            ## Find max value 
            highest_index = len(self.sa)-1  #avg sa
            highest_value = self.sa[-1][0]
            max_highest_index = len(self.sa)-1 # max sa
            max_highest_value = self.sa[-1][2]
            for i in xrange(-2, -len(self.sa)-1,-1):
                if highest_value - self.sa[i][0] <= self.EPSILON:
                    highest_index = i
                    highest_value = self.sa[i][0]
                if max_highest_value - self.sa[i][2] <= self.EPSILON:
                    max_highest_index = i
                    max_highest_value = self.sa[i][2]

            ## Summarize stats for specific avg SA
            sa_at_value = []    ## comm & steps values for a specific sa
            next_sa_to_search = self.sa_increment
            for i in xrange(len(self.sa)):
                if self.sa[i][0] >= next_sa_to_search:
                    sa_at_value.append (
                        {'sa': next_sa_to_search/self.NUM_FACTS,\
                         'comm': self.comm[i],\
                         'decisions': self.decisions[i],\
                         'correct_decisions': self.correct_decisions[i],\
                         'steps': self.steps[i]})
                    next_sa_to_search += self.sa_increment

            ## Now processs the SA for agent 0
            highest_index0 = len(self.sa0)-1  #avg sa
            highest_value0 = self.sa0[-1]
            max_highest_index0 = len(self.sa0)-1 # max sa
            max_highest_value0 = self.sa0[-1]
            for i in xrange(-2, -len(self.sa0)-1,-1):
                if highest_value0 - self.sa0[i] <= self.EPSILON:
                    highest_index0 = i
                    highest_value0 = self.sa0[i]

            sa0_at_value = []    ## comm & steps values for a specific sa
            next_sa_to_search = self.sa_increment
            for i in xrange(len(self.sa0)):
                if self.sa0[i] >= next_sa_to_search:
                    sa0_at_value.append (
                        {'sa': next_sa_to_search/self.NUM_FACTS,\
                         'comm': self.comm0[i],\
                         'commtotal': self.comm[i],\
                         'steps': self.steps[i]})
                    next_sa_to_search += self.sa_increment
        
            summary = { 'steps': self.steps[highest_index], \
                        'sa': highest_value/self.NUM_FACTS, \
                        'comm': self.comm[highest_index], \
                        'steps_maxsa': self.steps[max_highest_index], \
                        'maxsa': max_highest_value/self.NUM_FACTS, \
                        'comm_maxsa': self.comm[max_highest_index], \
                        'steps0': self.steps[highest_index0], \
                        'sa0': highest_value0/self.NUM_FACTS, \
                        'comm0': self.comm0[highest_index0], \
                        'commtotal0': self.comm[highest_index0], \
                        'sa_at_value': sa_at_value ,\
                        'sa0_at_value': sa0_at_value ,\
                        'total_filtered': self.total_filtered, \
                        'num_cc' : self.num_cc, \
                        'size_lcc' : self.size_lcc}
            return summary
