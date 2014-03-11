"""
    Contains information relevant to one agent's trust for another
    agent (target). Each trust component, competence (comp) and
    willingness (will) is modeled separately.

    trustee is the trustee of the trust relation (assuming the source is
    known already.)

    comp is given by a pair of true and untrue facts by a given
    person.

    will is given by a pair of mean/std of normally distributed trust
    values.

    category is one of good, selfish, spammer, incompetent

"""
import math
import random
from simutil import * 

class Trust(object):

    def __init__ ( self , trustee, \
                   prior_comp = ('M','M'), prior_will=('M','M')):
        self.trustee = trustee ## trustee of the trust
        self.comp = self.initial_comp(prior_comp)
        self.will = self.initial_will(prior_will)
        self.comp_history = {}
        self.comp_history[0] = self.comp
        self.will_history = {}
        self.will_history[0] = ([],self.will)
        self.will_data = []
        self.will_increment = 10 ##update will every xxx evidence updates
        self.will_forget = 10 ##forget the last xxx evidence updates
        self.trust = 1
        self.trust_uncertain = True
        self.is_trusted = False
        self.get_trust()  ## updates self.trust, self.trust_uncertain and self.is_trusted

    def __str__ ( self ):
        (a,b) = self.comp
        (c,d) = self.will
        return "(comp|will): ((%d,%d),(%.1f,%.1f))" \
            %( a,b,c,d )

    def initial_comp( self , (cat, unc)=(None,None) ) :
        ## setup is a list for low/medium/high uncertainty, 
        ## and each item is for low/medium/high competence category
        setup = {}
        setup[('L','L')] = (80,100)
        setup[('L','M')] = (5,8)
        setup[('L','H')] = (1,2)

        setup[('M','L')] = (100,100)
        setup[('M','M')] = (10,10)
        setup[('M','H')] = (1,1)

        setup[('H','L')] = (100,80)
        setup[('H','M')] = (8,5)
        setup[('H','H')] = (2,1)

        if cat != None:
            cat = cat.upper()
        else:
            cat = 'M'
        if unc != None:
            unc = unc.upper()
        else:
            unc = 'M'

        return setup[(cat,unc)] 

    def initial_will( self, (cat, unc)=(None,None) ) :
        mean_range = {}
        mean_range['H'] = 0.6
        mean_range['M'] = 0.5
        mean_range['L'] = 0.4

        std_range = {}
        std_range['H'] = 0.4
        std_range['M'] = 0.15
        std_range['L'] = 0.05

        if cat != None:
            cat = cat.upper()
        if unc != None:
            unc = unc.upper()

        if cat != None:
            cat = cat.upper()
        else:
            cat = 'M'
        if unc != None:
            unc = unc.upper()
        else:
            unc = 'M'

        return mean_range[cat], std_range[unc] 

    def get_comp_trust ( self ) :
        (g,b) = self.comp
        alpha = float(g)
        beta = float(b)
        mean = 1/(1+((beta+1)/(alpha+1)))
        std = math.sqrt(alpha*beta/( (alpha+beta)**2*(alpha+beta+1)))
        return (mean, std)

    def get_will_trust ( self ):
        return self.will

    def get_trust ( self ):
        """
        COMP |     X=3      |   Y=4  |   C=5           
             |              |        |           
        .75  |--------------|--------|--------- 
             |     X=3      |   Y=4  |   Y=4     
         .5  |--------------|--------|---------
             |              |        |           
             |     A=1      |   B=2  |   B=2     
             |              |        |           
             ---------------|--------|-------- WILL
                          .5        .75

        A=1: not competent and not willing, hoarder
        competent but not willing: selfish
        willing but not competent: incompetent
        
        good citizen : 5
        """

        mc_t1 = 0.6  #0.6
        mc_t2 = 0.8  #0.8
        mw_t1 = 0.6  #0.5
        mw_t2 = 0.8  #0.75
        (mc,sc) = self.get_comp_trust()
        (mw,sw) = self.get_will_trust()
        cat = None
        if mc <= mc_t1 and mw <= mw_t1:
            cat = 1 ## A: low trust
        elif mc <= mc_t1 and mw > mw_t1:
            cat = 2 ## B: medium trust, willing but not competent
        elif mc_t1 < mc and mw <= mw_t1:
            cat = 3 ## X: competence but not willing
        elif (mw_t1 < mw <= mw_t2 and mc > mc_t1) or \
             (mw > mw_t2 and mc_t1 < mc <= mc_t2):
            cat = 4 ## Y: above average willing and competent
        else:
            cat = 5 ## C: good citizen
        self.trust = cat
        if (sc > 0 and mc/sc < 5) and (sw > 0 and mw/sw < 1000):
            self.trust_uncertain = True
        else:
            self.trust_uncertain = False
        #print mc/sc, mw/sw
        self.is_trusted = self.find_if_trusted()

    def find_if_trusted( self ):
        ## When is someone trusted at all, used for filtering
        if self.trust in [1] and not self.trust_uncertain:
            return False
        else:
            return True

    def get_comp_evidence( self, time, ng, nb ):
        """ 
            Evidence is either 0 or 1, good or bad. 
            Time is the simulation time this evidence is obtained.
        """
        (g,b) = self.comp
        g += ng
        b += nb
        self.comp = (g,b)
        self.comp_history[time] = (ng,nb,g,b)


    def get_will_evidence( self, time, ev ):
        """ 
            Evidence is a value between 0 and 1.
            Time is the simulation time this evidence is obtained.
        """
        
        self.will_data.append(ev)
        if len(self.will_data) >= self.will_increment:
            (mu,su) = meanstd(self.will_data)
            if mu < 0:
                mu = 0
            elif mu > 1:
                mu = 1
            if su == 0:
                su = 0.001
            (m0,s0) = self.will
            if s0 == 0:
                s0 = 0.001
            numpts = 1
            ## numpts controls how much weight to give to each increment
            ## currently 1/10 of the increment.
            m = ((m0/s0**2)+(numpts*mu/su**2))/((1/s0**2)+(numpts/su**2))
            s = math.sqrt(1/((1/s0**2+numpts/su**2)))
            ## change the following to removing some items if
            ## we want to retain some history
            self.will = (m,s)
            self.will_history[time] = (self.will_data,self.will)
            self.will_data = self.will_data[self.will_forget:]

    def get_evidence( self, time, ng, nb, will_ev):
        """ 
            (ng,nb): Competence evidence (good, bad) is integer values.
            (will_ev): Willingness evidence is a value between 0 and 1.
            Time is the simulation time this evidence is obtained.
        """
        self.get_comp_evidence( time, ng, nb )
        self.get_will_evidence( time, will_ev )


if __name__ == '__main__':
    print "*********COMPETENCE TESTS*******"
    x = Trust('a',('h','h'),('l','h'))
    print str(x)

    print "Adding random positive/negative evidence, should end up with 0.5"
    (m,s) = x.get_comp_trust()
    print 'Start: %.4f %.4f' %(m,s)

    for i in range(20):
        ng = int(10*random.random())
        nb = int(10*random.random())
        x.get_comp_evidence(i, ng, nb)
        (m,s) = x.get_comp_trust()
        print "Evidence (%s,%s)" %(ng, nb), '%.4f %.4f' %(m,s)

    print "Adding specific evidence used in simulations"
    for z in ['L','M','H']:
        for (a,b) in [(50,0),(0,50),(0,500)]:
            print
            print "New trial"
            y = Trust('b',(z,'H'))
            print str(y)
            (m,s) = y.get_comp_trust()
            print 'Start: %.4f %.4f' %(m,s)
            y.get_comp_evidence(1,a,b)
            (m,s) = y.get_comp_trust()
            print "Evidence (%s,%s)" %(a, b), '%.4f %.4f' %(m,s)

    print
    print "*********WILLINGNESS TESTS*******"

    print "Using normally distributed evidence, first with mean 0.4, std 0.6"
    print "for 800 cases, then with mean 0.7, std 0.1 for 400 cases"
    for z in ['L','M','H']:
        print
        print "New trial"
        x = Trust('a',('h','h'),(z,'L'))
        (m,s) = x.get_will_trust()
        print 'Start: %.4f %.4f' %(m,s)

        for i in range(800):
            ev = random.normalvariate(0.4,0.6)
            x.get_will_evidence(i, ev)
            if i>1 and i%x.will_increment==1:
                (m,s) = x.get_will_trust()
                print  'New trust (%.4f, %.4f)' %(m,s)

        for i in range(400):
            ev = random.normalvariate(0.7,0.1)
            x.get_will_evidence(i, ev)
            if i>1 and i%x.will_increment==1:
                (m,s) = x.get_will_trust()
                print  'New trust (%.4f, %.4f)' %(m,s)

