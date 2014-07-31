from cmath import e, log

class Fact(object):

    def __init__ (ground_truth, id):

        self.ground_truth = ground_truth
        self.id = id
        self.decision = 0
        self.belief = 0.0
        self.disbelief = 0.0
        self.history = []
        
    def is_valuable():
        return self.ground_truth
        
    def id():
        return self.id

    def correct_bounds ():
        self.belief = max(min(self.belief, 1), 0)
        self.disbelief = max(min(self.disbelief, 1), 0)

    #When a fact is created, initialize the belief based on competence of agent
    def judgment(competence, model = 1):
        belief_error = random.uniform(0, 1-competence)
        if (model == 1):
            disbelief_error = random.uniform(0, belief_error)
        elif (model == 2):
            disbelief_error = random.gauss(1-competence, 1-competence)
            if (disbelief_error < 0):
                disbelief_error = 0
            elif (disbelief_error > 1):
                disbelief_error = 1
        else:
            disbelief_error = random.uniform(0, 1-competence)
        
        if (self.ground_truth == True):
            ## if competence == 1, (t,d) = (1,0)
            (t,d) = (1-belief_error, disbelief_error)
        else:
            ## if competence == 1, (t,d) = (0,1)
            (t,d) = (belief_error, 1-disbelief_error)

        (self.belief, self.disbelief) = (t,d)
        self.correct_bounds()

        self.history.append((self.belief, self.disbelief))

    #When a neighbor gives us a fact, use our belief in the neighbor and
    #their belief in the fact to get new information
    def propagate_belief():
        pass

    #Aggregate our history to recalculate belief and disbelief
    def aggregate_belief(nf_cognition):

        (b, d) = self.history[-1] #Look at most recent piece of evidence
        old_entropy = self.belief * log(self.belief) + self.disbelief * (self.disbelief) #Get our current entropy
        
        if(self.belief >= self.disbelief):
            new_entropy = -(self.belief + b) * log(self.belief + b) - \
                          (self.disbelief + (d * (1 - nf_cognition))) * log(self.disbelief + (d * (1 - nf_cognition)))
            if(new_entropy - old_entropy > nf_cognition*2.0/e): #Bias against entropy
                return
            self.belief += b
            self.disbelief += d * (1 - nf_cognition)

        else:
            new_entropy = -(self.belief + (b * (1 - nf_cognition))) * log(self.belief + (b * (1 - nf_cognition))) - \
                           (self.disbelief + d) * log(self.disbelief + d)
            if(new_entropy - old_entropy > nf_cognition*2.0/e): #Bias against entropy, normalize to max possible
                return
            self.belief += b * (1 - nf_cognition)
            self.disbelief += d
        

        self.correct_bounds()
        
    def decision():
        return self.decision

    #Make a decision based on our current evidence
    def decide(nf_cognition, nf_closure):
        if(self.decision != 0):
            return self.decision
        
        if((self.belief + self.disbelief) > nf_cognition):
            if((self.belief + nf_closure) > (self.disbelief + 1)):
                self.decision = 1
            if((self.disbelief + nf_closure) > (self.belief + 1)):
                self.decision = -1

        return self.decision

    #For sorting
    def __lt__(self, other):
        if (self.belief < other.belief):
            return true
        if (self.belief == other.belief and self.disbelief > other.disbelief):
            return true
        return false
