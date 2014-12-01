import simplejson as sj
import matplotlib.pyplot as plt
import pylab
import numpy as np
import sys
import glob
import GraphGen as gg
import networkx as nx
import random

marker_list = [  '*', 'o', 's', 'x', '<', '>', '|', '+', 'd', 'h', \
                ',', 'H', 'v', 'x', '*', 's', '<', '>', '|', \
                '+', 'd', 'h', ',', 'H', 'v' ]

linestyle_list = ['-', '--', '-.', ':', '-', '--', '-.', ':', '-', \
                  '--', '-.', ':', '-', '--', '-.', ':']

def sample_down(xval):
    targetsize = 12
    n = len(xval)
    if n <= targetsize:
        return np.array(xval)
    p = targetsize/float(n)
    newx = []
    xval.sort()
    newx.append(xval[0])
    for i in range(1,n-1):
        if random.random() <= p:
            newx.append( xval[i] )
    newx.append( xval[-1] )
    return np.array(newx)

    

def select_plot(alldensity, cc, bc, deg, label_type, plot_id,\
                compare_to=None, divide_by=None, outdir=""):
    """ plot_id: 0: sa, 1: comm, 2: steps """

    degree = 2
    for (centrality, allvalues) in [('cc',cc),('bc',bc),('deg',deg)]:
        fig = plt.figure()
        ax = fig.add_subplot(111)
        next = 0
        ## read graphs in increasing order of density
        allvals = []
        for key in allvalues:
            allvals.append( (float(alldensity[key]), key) )
        allvals.sort()
        ## for each graph type, construct x and y values
        for (val, graph_name) in allvals:
            if graph_name.find('rand_0.03') != -1 and outdir == 'g20_twitter':
                continue
            x = []
            y = []
            for val in allvalues[graph_name]:
                if compare_to == None:
                    if divide_by == None:
                        newval = val[plot_id]
                    else: ##normalizing
                        newval = float(val[plot_id])/val[4][divide_by]
                else:
                    if divide_by == None:
                        newval = val[plot_id]/float(val[compare_to])
                    else:
                        newval = float(val[plot_id])/val[4][divide_by]
                if label_type == 'comm_per_sa_gain':
                    newval = val[plot_id]/float(val[compare_to])
                    normfactor = float(val[4]['comm'])/val[4]['sa']
                    newval = newval/normfactor
                #### Comm gains
                if label_type.find('comm') != -1 and \
                   label_type.find('gain') != -1 and newval != 0:
                    newval = 1/newval
                if newval != 0:
                    x.append(val[0])
                    y.append(newval)

            xval = x[:]
            ## find a fit for the y values
            x = np.array(x)
            y = np.array(y)
            z = np.polyfit(x, y, degree)
            p = np.poly1d(z)
            gname_wdensity = graph_name + "__" + alldensity[graph_name]
            xnew = sample_down(xval)
            ax.plot(xnew,p(xnew), label=gname_wdensity, marker=marker_list[next])
            ##linestyle = linestyle_list[next])
            ##end of trendline
            next += 1

        #ax.legend(loc='upper center', bbox_to_anchor=(0.5, 0.1),
        #          ncol=3, fancybox=True, shadow=True,\
        #          labelspacing=0.1)
        plt.xlabel ( centrality )
        plt.ylabel ( label_type )
        plt.ylim( ymin=0 )
        plt.xlim( xmin=0 )
        plt.xlim( xmax=1 )
        outfname = "figs/%s/%s_%s.pdf" %(outdir, centrality, label_type)
        print "Saving file:", outfname
        plt.savefig( outfname, bbox_inches='tight' )
        

        lgd = plt.figure() 
        handles, labels = ax.get_legend_handles_labels()
        lgd.legend(handles, labels)

        lgd.savefig("figs/%s/legend.pdf" %outdir, \
        bbox_inches=lgd.get_window_extent().transformed(lgd.dpi_scale_trans.inverted()))
        
        plt.close( "all" )


def extract(sa_at_value):
    #print sa_at_value
    for val in sa_at_value:
        if val['sa'] == 0.8:
            return val['comm'], val['steps']
    return (0,0)

def get_avg_density(m):
    import networkx as nx
    n = m["setup"]["num_agents"]
    avgdensity = 0.0
    obj = range(n) #What is this for?
    for i in range(n): #why 10? n makes more sense
        avgdensity += m['dens'] #I changed this to get it directly (no graph recalculation).
    return "%.2f" %(avgdensity/n)

def get_graph_name(m):
    gtype = m["graph_type"]
    n = m["setup"]["num_agents"]
    a = m["setup"]["alpha"]
    b = m["setup"]["beta"]
    s = m["setup"]["kron_seed_self_loops_stochastic"]
    name = "%s_%s_%s_%s_%s" %(gtype, n, a, b, s) # This is specifically for Kronecker, Technically we dont need the other stuff for this file
    return name

def add_stats(stats, gname, cc,bc,deg):
    if gname not in cc:
        cc[gname] = []
    cc[gname].extend(stats['cc'])
    if gname not in bc:
        bc[gname] = []
    bc[gname].extend(stats['bc'])
    if gname not in deg:
        deg[gname] = []
    deg[gname].extend(stats['deg'])

def sort_stats(cc,bc,deg):
    for key in cc:
        cc[key].sort()
    for key in bc:
        bc[key].sort()
    for key in deg:
        deg[key].sort()

def process_file(fname, cc, bc, deg, alldensity):
    sa = {}
    old_gname = None
    lineno = 0
    initial_stats = {}
    stats = {'cc':[], 'bc':[], 'deg':[]}
    for line in open(fname):
        lineno += 1
        if lineno == 1:
            continue
        m = sj.loads(line)
        gname = get_graph_name(m)
        if len(m["node_stats"].keys())==0:
            alldensity[gname] = get_avg_density(m) #this is where we get denisty
            initial_stats['sa'] = m['summary_results']['sa']
            initial_stats['comm'] = m['summary_results']['comm']
            initial_stats['steps'] = m['summary_results']['steps']
            continue
        if gname != old_gname:
            if old_gname != None:
                add_stats(stats, old_gname, cc, bc, deg)
                stats = {'cc':[], 'bc':[], 'deg':[]}
                initial_stats = {}
            old_gname = gname
            
        comm = m['summary_results']['comm']
        steps = m['summary_results']['steps']
        stats['cc'].append( (m['node_stats']['cc'],\
                             m['summary_results']['sa'],\
                             comm, steps, initial_stats) )
    
        stats['bc'].append( (m['node_stats']['bc'],\
                             m['summary_results']['sa'], \
                             comm, steps, initial_stats) )
    
        stats['deg'].append( (m['node_stats']['deg'],\
                              m['summary_results']['sa'],\
                              comm, steps, initial_stats) )

    add_stats(stats, old_gname, cc, bc, deg)
    

if __name__ == "__main__":
    cc = {}
    bc = {}
    deg = {}
    alldensity = {}

    for fname in glob.glob("C:/Users/Benjamin/Desktop/SKG Fast/kronresults/*.txt"):
        process_file(fname, cc, bc, deg, alldensity)
        
    outdir = 'multi_output'
    select_plot(alldensity, cc, bc, deg, 'sa_gain', 1, compare_to=None, divide_by='sa', outdir=outdir)
    select_plot(alldensity, cc, bc, deg, 'comm_gain', 2, compare_to=None, divide_by='comm', outdir=outdir)
    #select_plot(alldensity, cc, bc, deg, 'steps', 3, compare_to=None, divide_by='steps', outdir=outdir)
    select_plot(alldensity, cc, bc, deg, 'comm_per_sa', 2,compare_to=1,divide_by=None, outdir=outdir)
    select_plot(alldensity, cc, bc, deg, 'comm_per_sa_gain', 2,compare_to=1,divide_by=None, outdir=outdir)

    # select_plot(alldensity, cc, bc, deg, 'steps_vs_sa', 3,compare_to=1, divide_by=None, outdir=outdir)


