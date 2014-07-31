
"""
.. py:class:: Agent

   .. automethod:: __init__

Class for generating and implementing Agents.

:param int numfacts: number of facts in the simulation 
 that are valuable

:param int numnoise: number of facts in the simulation 
 that are noise

:param float will: how frequently an agent will act
:param float comp: how frequently the agent will a fact 
 as valuable or not correctly (1: always, p: 
 p% of the time)

:param float spam:  how frequently the agent will send the 
 same fact to the same person (1 always, 0 never)

:param float selfish: how frequently the agent will drop 
 a fact and not send at all to a specific person 
 (0 never, 1 always)

:param int capacity: how many actions an agent can take 
 at each simulation step, 1 by default to implement 
 agents with limited cognitive resources.

:param Boolean trust_used: If True (default), keeps statistics 
 about Trust and sorts outbox by how much each neighbor is trusted 
 
:param Boolean inbox_trust_sorted: If True (default), periodically
 sorts the inbox by trust, processing facts from trusted neighbors
 first

:param Boolean trust_filter_on: If True (default), it only sends
 messages out to neighbors that are minimally trusted, the rest
 are filtered out.

:param Boolean uses_knowledge: True (default) if agent uses
 knowledge based processing and sends only facts it considers
 valuable. If False: it sends all facts regardless of value, used
 for hierarchical processing.

"""

import random 
import Trust
import Fact
from simutil import *

class Agent(object):

    def __init__ (self, w=1, c=1, numfacts = 0, numnoise=0, \
                  spammer=0, selfish=0,  \
                  trust_used = True, inbox_trust_sorted = True, \
                  trust_filter_on = True, capacity = 1, uses_knowledge=True):
        ## General constants used in simulation
        self.NUM_FACTS = numfacts
        self.NUM_NOISE = numnoise

        ## Agent properties
        self.trust_used = trust_used
        self.inbox_trust_sorted = inbox_trust_sorted
        self.willingness = w
        self.competence = c
        self.selfish = selfish
        self.spammer = spammer
        self.capacity = capacity
        self.trust_filter_on = trust_filter_on
        self.uses_knowledge = uses_knowledge 
        # for hierarchy, all facts are considered valuable without
        # considering competence!
        self.spam_sensitivity = 0.2  # discount for spam behavior
        # how much spamming will be counted as negative competence evidence

        ## Action history
        self.inbox = []  ## list of (fact, sender_neighbor=None)
        self.outbox = []  ## list of (trust_for_receiver, fact, receiver) 
        self.last_received_facts = []
        self.all_received_facts = set([])
        ## all facts sent once to someone, used for performance optimization
        self.sentfacts = set([])  
        self.numsent = 0 ## number of facts sent
        self.knowledge = set([]) ## id of all facts known, spam or valuable
        self.history = {} ## key:fact, value: set of neighbors fact is sent to
        self.time_spent = 0 ## simulation time, number of times act is executed
        self.trust_update_frequency = 10

        ## Network based properties, beliefs
        self.neighbors = set([])
        self.trust = {}  ## Key: neighbor, Value: Trust object
        self.neighbor_spamminess = {}
        self.num_filtered = 0
        
        self.nf_cognition = 1
        self.nf_closure = 1

    def clear (self):
        """Clears all history, but leaves intact personal properties."""
        self.inbox = []  ## list of (fact, sender_neighbor=None)
        self.outbox = []  ## list of (trust_for_receiver, fact, receiver) 
        self.last_received_facts = []
        self.all_received_facts = set([])
        ## all facts sent once to someone, used for performance optimization
        self.sentfacts = set([])  
        self.numsent = 0 ## number of facts sent
        self.knowledge = set([]) ## id of all facts known, spam or valuable
        self.history = {} ## key:fact, value: set of neighbors fact is sent to
        self.time_spent = 0 ## simulation time, number of times act is executed
        self.trust_update_frequency = 10

        ## Network based properties, beliefs
        self.trust = {}  ## Key: neighbor, Value: Trust object
        self.neighbor_spamminess = {}
        self.num_filtered = 0

    def get_trust_for_neighbors( self ):
        line = ""
        for n in self.neighbors:
            line += "%d/%r " %(self.trust[n].trust, self.trust[n].is_trusted)
        return line

    def add_fact(self, fact):
        """ Add fact to knowledge. """
        self.knowledge.add(fact)

    def connect_to(self, neighbors, \
                   prior_comp = ('M','M'), \
                   prior_will=('M','M')):
        """ 
            Connects the agent to a set of other agents.

            Example usage::

                a.connect_to(neighbors, ('M','L'), ('H','H'))

            Create a link to all Agents in the set neighbors.
            Initialize prior trust for all neighbors if prior
            competence and willigness is given.

            :param neighbors: a set of Agent objects
             that are neighbors of the current Agent

            :param prior_comp: prior competence
             belief for all neighbors, given as a pair of belief and
             uncertainty values, each one of 'L','M','H' for low
             medium and high. See :mod:`Trust` for more details.

            :param prior_will: prior competence
             belief for all neighbors, same format as prior_comp.

        """
        self.neighbors = set(neighbors)
        if self.trust_used or self.trust_filter_on or self.inbox_trust_sorted:
            for n in self.neighbors:
                self.trust[n] = Trust.Trust(n, prior_comp, prior_will)
                self.neighbor_spamminess[n] = 0

    def stat(self):
        """ Return basic stats for the agent. """
        return (len(self.knowledge), len(self.neighbors))

    def is_fact_valuable(self,fact):
        """ Return the ground truth of whether the fact is
        valuable. """
        return fact.is_valuable()
        
    def fact_index(self, id):
        for index, fact in enumerate(self.knowledge):
            if (fact.id() == id):
                return index
        return -1

    def process_fact(self, fact, sender_neighbor):
        ## sender_neighbor is None if the fact is from initial inbox 
        
        # Determine if the fact is valuable
        index = self.fact_index(fact.id())
        
        if(index == -1): #This is our first time seeing it
            fact = Fact.Fact(fact.is_valuable(), fact.id()) #Reinitialize, and add to knowledge
            fact.judgment()
            self.add_fact(fact)
            index = len(self.knowledge) - 1
            
        if(sender_neighbor and not (fact.id(), sender_neighbor) in self.all_received_facts): #We got this from a neighbor, so deal with new information
            self.knowledge[index].propagate_belief()
            self.knowledge[index].aggregate_belief(self.nf_cognition)
            self.knowledge[index].decide(self.nf_cognition, self.nf_closure)
            
        

        # If trust is considered, add this fact as evidence and spamminess
        if self.trust_used:
            if sender_neighbor: ## there is a sender for the fact
                ## there is no sender for initial facts
                self.last_received_facts.append( (sender_neighbor, self.knowledge[index].decision()) )
                if (fact.id(), sender_neighbor) in self.all_received_facts:
                    self.neighbor_spamminess[sender_neighbor] += 1
                else:
                    self.all_received_facts.add((fact.id(), sender_neighbor))
                if len(self.last_received_facts) > self.trust_update_frequency:
                    self.process_trust()

        ## Decide who to send the fact to based on spamminess and selfishness
        if self.knowledge[index].decision():
            if self.spammer > 0:
                ## x% spammer person will send the same fact to x% of contacts.
                already_sent_tmp = list(self.history.get(fact.id(),set()))
                template = range(len(already_sent_tmp))
                random.shuffle(template)
                idx = int(len(template) * (1-self.spammer))
                already_sent  = []
                for i in template[:idx]:
                    already_sent.append( already_sent_tmp[ template[i]] )
                already_sent = set(already_sent)
            else:
                already_sent = self.history.get(fact.id(),set())

            to_send = []
            to_send_tmp = self.neighbors - already_sent
            to_send_tmp = list(to_send_tmp)

            template = []

            ##selfishness code
            if self.trust_used: ##construct template based on trust
                ## and exclude people if trust filter is on
                for i in range(len(to_send_tmp)):
                    n = to_send_tmp[i]
                    if self.trust_filter_on: ##only included trusted people
                        if self.trust[n].is_trusted:
                            template.append( (self.trust[n].trust, i) )
                        else:
                            self.num_filtered += 1
                    else:
                        template.append( (self.trust[n].trust, i) )
                ## choose the least trusted people from to_send_tmp to exclude
                template.sort()
                idx = int(len(template) * (1-self.selfish))
                
                ## find the items to send, sort by trust if trust is used
                for (t,i) in template[:idx]:
                    to_send.append( (t, fact.id(), to_send_tmp[i]) )
                to_send.sort(reverse = True)
            else:  ## no trust used
                if self.selfish > 0:
                    for i in range(len(to_send_tmp)):
                        n = to_send_tmp[i]
                        if random.random() <= (1-self.selfish):
                            to_send.append( (1, fact.id(), to_send_tmp[i]) )
                else:
                    for i in range(len(to_send_tmp)):
                        n = to_send_tmp[i]
                        to_send.append( (1, fact.id(), to_send_tmp[i]) )

            self.outbox.extend( to_send )

    def init_outbox(self):
        """ Add all initial knowledge as a fact to send out. """
        for fact in self.knowledge:
            self.process_fact(fact, None) ## There is no sender

    def receive(self, fact, neighbor):
        """ Receive a fact from another neighbor. """
        self.inbox.append((fact, neighbor))

    def act(self):
        """ 
             A single action for the agent:
             - either send something from the outbox, or
             - receive something from the inbox if outbox is empty.

        """
        debug = True
        self.time_spent += 1 ## simulation time incremented
        actions_taken = []
        for i in xrange(self.capacity):
            ### By willingness probability, decide whether to act or not
            if random.random() <= self.willingness:
                ## Agent decided to act
                decision = self.decide_action()
                if decision == 'outbox':
                    ### Take the first action from the outbox
                    self.numsent += 1
                    (trust, fact, n) =  self.outbox.pop(0)
                    if fact in self.sentfacts:
                        self.history[fact].add(n)
                    else:
                        self.history[fact] = set([n])
                    self.sentfacts.add(fact)
                    actions_taken.append((n, self.knowledge[self.fact_index(fact)]))
                elif len(self.inbox) != 0: # decision is inbox
                    ### Process the first fact in the inbox and queue to outbox 
                    (fact, neighbor) = self.inbox.pop(0)
                    self.process_fact(fact, neighbor)
        return actions_taken  ## No send action was taken

    def decide_action(self) :
        ## choose outbox as long as there is something there.
        # if len(self.outbox) != 0 and len(self.inbox) != 0:
        #     if random.random() < 0.5:
        #         return "outbox"
        #     else:
        #         return "inbox"
        # elif len(self.outbox) != 0:
        #     return "outbox"
        # else:
        #     return "inbox"
        if len(self.outbox) != 0:
            return "outbox"
        else:
            return "inbox"
        

    def sort_inbox_by_trust(self) :
        """ 
             Sort the inbox according to the current trust value of 
             each neighbor, send to most trusted first. Called from 
             process_trust, after updating trust if a flag is set.
             We will simply take the trusted agents' message and put
             them to top!

        """
        new_inbox = []
        unsorted_inbox = []
        for (fact, sender) in self.inbox:
            if self.trust[sender].is_trusted:
                new_inbox.append( (self.trust[sender].trust, fact, sender) )
            else: 
                unsorted_inbox.append( (fact, sender) )
        new_inbox.sort(reverse = True)
        self.inbox = []
        for (t, fact, sender) in new_inbox:
            self.inbox.append( (fact, sender) )
        self.inbox.extend(unsorted_inbox)

    def sort_outbox_by_trust(self) :
        """ 
             Sort the outbox according to the current trust value of 
             each neighbor, send to most trusted first. Called from 
             process_trust, after updating trust.

        """
        new_outbox = []
        for (trust, fact, neighbor) in self.outbox:
            new_outbox.append( (self.trust[neighbor].trust, fact, neighbor) )
        new_outbox.sort(reverse = True)
        self.outbox = new_outbox

    def process_trust(self) :
        """
             After a certain amount of evidence is collected, 
             update trust for each neighbor and resort the outbox.
        """

        num_evidence = float(len(self.last_received_facts))
        evidence = {}
        for n in self.neighbors:
            evidence[n] = [0,0,0]
        for (n, is_good) in self.last_received_facts:
            evidence[n][0] += 1
            if is_good:
                evidence[n][1] +=1
            else:
                evidence[n][2] += 1

        all_will_evidence = []
        for n in self.neighbors:
            all_will_evidence.append ( evidence[n][0]/num_evidence )
            evidence[n][2] += self.spam_sensitivity * self.neighbor_spamminess[n]

        (m,s) = meanstd(all_will_evidence)
        for n in self.neighbors:
            x = evidence[n][0]/num_evidence 
            ev = 0
            if x > m+s:
                ev = 1
            elif x >= m:
                ev = 0.75
            elif x >= m-s:
                ev = 0.5
            elif x >= m-2*s:
                ev = 0.25
            self.trust[n].get_will_evidence(self.time_spent, ev)
            self.trust[n].get_comp_evidence(self.time_spent, \
                                            evidence[n][1], \
                                            evidence[n][2])
            self.trust[n].get_trust()  ## Update trust category for neighbor

        self.last_received_facts = []
        self.sort_outbox_by_trust()
        if self.inbox_trust_sorted:
            self.sort_inbox_by_trust()
