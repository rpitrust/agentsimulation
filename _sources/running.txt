
Running the taNdem simulation model
====================================

There are alternate ways to run the simulation model. The methods go
from easiest but less configurable to the most configurable
options. The simulation package requires:

-  Python 2.7 (any Python 2 version should work, but it is only tested
   on 2.7)

-  The ``networkx`` module, installable by easy_install:

   http://networkx.github.io/documentation/latest/

-  The ``simplejson`` module (only required for use in the runner
   module for the use of configuration files) , installable by
   easy_install:

   http://simplejson.readthedocs.org/en/latest/


Running by configuration files
---------------------------------

It is possible to run the agent simulation with the help of a runner
utility that makes use of a configuration file that sets various
parameters. The input configuration is given in the simplejson format,
and provides output in the simplejson format. 

Each configuration file the parameters to be varied in the given
simulation series. To run, use::

   python runner.py config_file output_file


Example configuration file::

    {
    "description": "Example file"
    , "num_facts"      : [50]
    , "num_noise"      : [50,500,5000]
    , "num_agents"     : [20]
    , "agent_per_fact" : [1]
    , "num_steps"      : 10000
    , "trust_used"     : true
    , "trust_filter_on"     : true
    , "inbox_trust_sorted" : false
    , "competence"     : [0.2,0.4,0.6,0.8,1.0]
    , "willingness"    : [0.8,1.0]
    , "spamminess"     : [0,0.1]
    , "selfishness"    : [0,0.8]
    , "num_trials"     : 20
    , "graph_description" : [ 
                { "type": "spatial_random"
                , "radius" : 0.5 } ]
    , "agent_setup"    : [
               []
      	       , [{ "ratio":0.1, "competence":1, "willingness":0.2 }, 
                  { "ratio":0.2, "selfishness":0.4 } ]
               , [{ "ratio":0.2, "competence":1, "selfishness":0.2 }]  
              ]
      } 


In this file, various parameters are being varied for competence,
willingness, spamminess and selfishness (a total of 5x2x2x2=40
cases). For each case, a random subset of the agents can have varying
characteristics given in the ``agent_setup`` parameters. We have three
settings in this case, so a total of 120 different tests will be
run. Each test will run 10,000 steps and will be repeated for 20
times. 

Note that other parameters do not take as input list of values at this
point.

The output is also a simplejson file listing results for each of the
120 cases tested here.

Running case by case
------------------------

It is possible to run a single configuration of agent properties using
tester code found in tester.py. This file shows how to use the
simulation package for a specific configuration. For each
configuration, a specific set of statistics can be printed. Run this
using::

   python tester.py


Further configuration of agent cases
-------------------------------------

The above options do not make it possible to modify various
characteristics of the agents, such as initial trust of specific
agents. These options are not currently exposed in the simulation
module for ease of use. As a result, changing of the simulation code
is required for such tests. More detailed information is available in
the simulation module found in: ``simulation.py``.
