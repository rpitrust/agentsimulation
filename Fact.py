class Fact(object):

    def __init__ (valuable = True):

        self.valuable = valuable
        self.trust = 0.0
        self.distrust = 0.0
        self.history = []

    def correct_bounds ():
        if (self.trust < 0):
            self.trust = 0.0
        if (self.distrust < 0):
            self.distrust = 0.0
        if (self.trust > 1):
            self.trust = 1.0
        if (self.distrust > 1):
            self.distrust = 1.0

    #When a fact is created, initialize the belief based on competence of agent
    def initialize_belief(competence, model = 1):
        trust_error = random.uniform(0, 1-competence)
        if model == 1:
            distrust_error = random.uniform(0, trust_error)
        elif model == 2:
            distrust_error = random.gauss(1-competence, 1-competence)
            if distrust_error < 0:
                distrust_error = 0
            elif distrust_error > 1:
                distrust_error = 1
        else:
            distrust_error = random.uniform(0, 1-competence)
        
        if self.valuable == True:
            ## if competence == 1, (t,d) = (1,0)
            (t,d) = (1-trust_error, distrust_error)
        else:
            ## if competence == 1, (t,d) = (0,1)
            (t,d) = (trust_error, 1-distrust_error)

        (self.trust, self.distrust) = (t,d)
        self.correct_bounds()

        ##TODO
        ##Right now, we take our own perception as the same as a neighbor
        ##agent who we give full trust to. This should be changed.
        self.history.append((self.trust, self.distrust))

    #Use KAAV method from Practical aggregation operators by Victor et al
    def aggregate_trust_kaav(gamma):

        w_denom = 0.0
        self.trust = 0.0
        self.distrust = 0.0
        
        for (t,d) in self.history:
            w_denom += pow((t+d),gamma)

        for (t,d) in self.history:
            self.trust += t * pow((t+d)/w_denom,gamma)
            self.distrust += d * pow((t+d)/w_denom,gamma)

    #Aggregate our history to recalculate trust and distrust
    def aggregate_trust(model = 'KAAV'):

        if(model == 'KAAV'):
            self.aggregate_trust_kaav(1)

        self.correct_bounds()

    #Need a T-norm and T-conorm for propagation. Feel free to change
    def T(x, y):
        return x*y
    def S(x, y):
        return x+y - x*y

    #When a neighbor gives us a fact, use our trust in the neighbor and
    #their trust in the fact to get new information
    def propagate_trust(n_trust, n_dtrust, f_trust, f_dtrust, model):

        if (model == 1): #Method 4 from Victor et al
            (t, d) = ( T(n_trust, f_trust),
                       S(T(n_trust, f_dtrust),T(n_dtrust, f_trust)) )

        self.history.append(t, d) #Add our new info to our history
        self.aggregate_trust() #Aggregate our history into new trust values

    #For sorting
    def __lt__(self, other):
        if (self.trust < other.trust):
            return true
        if (self.trust == other.trust and self.distrust > other.distrust):
            return true
        return false
