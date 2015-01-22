
"""
.. py:class:: SimpleAgent

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

:param Boolean uses_knowledge: True (default), does nothing

"""

import random 
import Trust
from simutil import *

class SimpleAgent(object):

    def __init__ (self, w=1, c=1, numfacts = 0, numnoise=0, \
                  spammer=0, selfish=0,  \
                  trust_used = False, inbox_trust_sorted = False, \
                  trust_filter_on = False, capacity = 1, \
                  uses_knowledge=True, twitter_model=False ):
        ## General constants used in simulation
        self.NUM_FACTS = numfacts
        self.NUM_NOISE = numnoise

        ## Agent properties
        self.willingness = w
        self.competence = c
        self.selfish = selfish
        self.spammer = spammer
        self.capacity = capacity

        ## Action history
        self.inbox = []  ## list of (fact, sender_neighbor=None)
        self.outbox = []  ## list of (trust_for_receiver, fact, receiver) 
        ## all facts sent once to someone, used for performance optimization
        self.numsent = 0 ## number of facts sent
        self.knowledge = set([]) ## id of all facts known, spam or valuable
        self.facts_known = set([])
        self.time_spent = 0 ## simulation time, number of times act is executed

        self.history = {} ## key:fact, value: set of neighbors fact is sent to
        for fact in range(self.NUM_FACTS + self.NUM_NOISE):
            self.history[fact] = set()
        
        ## Network based properties, beliefs
        self.neighbors = set([])
        self.num_filtered = 0
        self.twitter_model = twitter_model

    def clear (self):
        """Clears all history, but leaves intact personal properties."""
        self.inbox = []  ## list of (fact, sender_neighbor=None)
        self.outbox = []  ## list of (trust_for_receiver, fact, receiver) 
        ## all facts sent once to someone, used for performance optimization
        self.numsent = 0 ## number of facts sent
        self.knowledge = set([]) ## id of all facts known, spam or valuable
        self.facts_known = set([]) ## id of all valuable facts known
        self.time_spent = 0 ## simulation time, number of times act is executed
        for fact in range(self.NUM_FACTS + self.NUM_NOISE):
            self.history[fact] = set()


    def add_fact(self, fact, is_good):
        """ Add fact to knowledge. """
        self.knowledge.add(fact)
        if is_good:
            self.facts_known.add(fact)

    def connect_to(self, neighbors, \
                   prior_comp = None, \
                   prior_will = None):
        """ 
            Connects the agent to a set of other agents.

            Example usage::

                a.connect_to(neighbors, ('M','L'), ('H','H'))

            Create a link to all Agents in the set neighbors.
            Initialize prior trust for all neighbors if prior
            competence and willigness is given.

            :param neighbors: a set of Agent objects
             that are neighbors of the current Agent


        """
        self.neighbors = set(neighbors)

    def stat(self):
        """ Return basic stats for the agent. """
        return (len(self.knowledge), len(self.neighbors))

    def is_fact_valuable(self,fact):
        """ Return the ground truth of whether the fact is
        valuable. """
        if (0 <= fact < self.NUM_FACTS):
            return True
        else:
            return False

    def tweet_fact(self, fact, neighbor):
        # Determine if the fact is valuable
        is_good = self.is_fact_valuable(fact)
        known = fact in self.facts_known
        
        if random.random() > self.competence:
            ## process fact incorrectly
            thinks_good = not is_good
        else:
            thinks_good = is_good
        
        actions_taken = []
        ## Send to everyone, broadcast model as long as this is a new fact
        if thinks_good and not known:
            self.add_fact(fact, is_good)
            for n in self.neighbors:
                self.numsent += 1
                self.history[fact].add(n)
                actions_taken.append((n, fact))
        return actions_taken

    def process_fact(self, fact, sender_neighbor):
        ## sender_neighbor is None if the fact is from initial inbox 
        
        # Determine if the fact is valuable
        is_good = self.is_fact_valuable(fact)
        self.add_fact(fact, is_good)
        if random.random() > self.competence:
            ## process fact incorrectly
            is_good = not is_good

        ## Decide who to send the fact to based on spamminess and selfishness
        if is_good:
            if self.spammer > 0:
                ## x% spammer person will send the same fact to x% of contacts.
                already_sent_tmp = list(self.history[fact])
                template = range(len(already_sent_tmp))
                random.shuffle(template)
                idx = int(len(template) * (1-self.spammer))
                already_sent  = []
                for i in template[:idx]:
                    already_sent.append( already_sent_tmp[ template[i]] )
                already_sent = set(already_sent)
            else:
                already_sent = self.history[fact]

            ##selfishness code
            if self.selfish > 0:
                for n in (self.neighbors - already_sent):
                    if random.random() <= (1-self.selfish):
                        self.outbox.append( (1, fact, n) )
            else:
                for n in (self.neighbors - already_sent):
                    self.outbox.append( (1, fact, n) )


    def init_outbox(self):
        """ Add all initial knowledge as a fact to send out. """
        for fact in self.knowledge:
            self.inbox.append( (fact, None) )
            #self.process_fact(fact, None) ## There is no sender

    def receive(self, fact, neighbor):
        """ Receive a fact from another neighbor. """
        if self.twitter_model: ## insert to the top
            self.inbox.insert(0, (fact, neighbor))
        else:
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
                if self.twitter_model:
                    if len(self.inbox) != 0: # decision is inbox
                        ### Process the first fact in the inbox and
                        ### immediately send to all the neighbors
                        (fact, neighbor) = self.inbox.pop(0)
                        actions_taken = self.tweet_fact(fact, neighbor)
                else:
                    if len(self.outbox) != 0: ##outbox is not empty:
                        ### Take the first action from the outbox
                        self.numsent += 1
                        (trust, fact, n) =  self.outbox.pop(0)
                        self.history[fact].add(n)
                        actions_taken.append((n, fact))
                    elif len(self.inbox) != 0: # decision is inbox
                        ### Process the first fact in the inbox and queue to outbox 
                        (fact, neighbor) = self.inbox.pop(0)
                        self.process_fact(fact, neighbor)
        return actions_taken  ## No send action was taken
