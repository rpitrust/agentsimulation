
Overview of the taNdem Simulation Package
==========================================

This package implements an agent scenario in which agents share
information with each other in a networked setting. The package
incorporates many adjustable parameters that are easily extensible. We
give an overview of these characteristics in this document.

The code is available on:

   https://github.com/rpitrust/agentsimulation

Agent Connectivity
-----------------------

Agents are connected to each other through a network that determines
their connectivity. Each edge is currently of the same strength and/or
bandwidth. The connectivity can be generated using different
algorithms. Currently, we have two basic methods:

-  **Random graphs** (Erdos–Renyi) of a given connection probability

-  **Spatial random graphs** in which agents are distributed in a one by
   one grid. The connection prbability is then given by a radius. All
   nodes with distance within a given radius are connected.

-  **Hierarchy** implements a single hierarchy of three levels, leader
   (agent 0), second level managers and employees.

The :mod:`GraphGen` module implements this function:

   https://github.com/rpitrust/agentsimulation/blob/master/GraphGen.py

Agent Behavior Characteristics
-------------------------------

Agents have characteristics that determine their behaviors. These
characteristics are summarized below.

-  **Competence** describes the ability to discern signal from noise
   in information

-  **Willingness** describes the percentage of time the agent will
   perform an action. Willingness can model the reliability of the
   agent or the attention they can give to a specific problem.

-  **Capacity** describes the number of actions the agent is able to
   take at each step of the simulation, if it is willing. Capacity is
   set to 1 by default.

-  **Spamminess** describes the percentage of the time the agent will
   spam a neighbor by sending the same information. By default, agents
   do not spam.

-  **Selfishness** describes the percentage of the neighbors the agent
   will share information with, instead of keeping it to
   self. Selfishness describes whether agent will act in self-interest
   or in the interest of the network. Agents are not selfish by default.

-  **Trust** characteristics describe whether the agent uses trust to 
   to filter who to send messages to (outbox filtering) and order messages 
   from other agents (inbox sorting). The trust can be turned on (default)
   or off. 

-  **Spam sensitivity** describes how much the agent considers spamming 
   behavior of others as a measure of their incompetence axis of trust. 
   Depending on the scenario, this can be adjusted. When set to zero, 
   spamming of others does not effect the trust ratings.

The :class:`Agent` module sets these parameters.

   https://github.com/rpitrust/agentsimulation/blob/master/Agent.py


 
Trust
--------

Agents can base their behavior based on trust. In this case, they need
to assess their trust for others based on their prior trust and
evidence. An agent's trust belief for another agent consist of two
components:

-  **Competence** is the belief that the other agent has the ability
   to distinguish signal from noise. The competence belief is given
   with a prior value, i.e. initial belief, and evidence obtained
   within the simulation. The initial belief is given by a trust value
   and associated uncertainty. If uncertainty is low, new evidence
   will have little effect in the given belief. The evaluation of
   evidence is tied to the agent's competence: a person who can tell
   signal from noise can also better judge other agents' competence.

-  **Willingness** is the belief that the other agent will dedicate
   their energy to sending the agent information, instead of helping
   others or serving self-interest. Willingness models rational
   reciprocal information sharing behavior. It is seeded with a prior
   belief and associated uncertainty. If uncertainty is very low,
   simulation based evidence has no effect on willingness
   beliefs. Unlike competence, willingness beliefs are relative to
   others. When there is no information to share, then agents share
   nothing. This does not impact the beliefs about their willingness
   negatively. 

-  Both beliefs are used to determine whether an agent can be
   trusted. Currently, the competence and willingness levels are used
   to determine a qualitative rating of trust, as given by the table
   below:

   +------------------+----------------+-----------+-----------+
   | Comp > 0.8       |    T = 3       | T = 4     | T = 5     |
   +------------------+----------------+-----------+-----------+
   | Comp <=   0.8    |    T = 3       | T = 4     | T = 4     |
   |                  |                |           |           |
   +------------------+----------------+-----------+-----------+
   | Comp <=   0.6    |                |           |           |
   |                  |    T = 1       | T = 2     | T = 2     |
   |                  |                |           |           |
   |                  |                |           |           |
   +------------------+----------------+-----------+-----------+
   |   0              |   Will <= 0.6  | Will      | Will      |
   |                  |                | <= 0.8    | > 0.8     |
   +------------------+----------------+-----------+-----------+

   Note that the thresholds can be changed in the :mod:`Trust`  module:

   https://github.com/rpitrust/agentsimulation/blob/master/Trust.py

   In this case, trust values go from 5 (highest) to 1 (lowest). Trust
   value of 1 is considered not trust. We current do not model
   distrust in the simulation.

The trust module allows new evidence to be entered periodically and
old evidence to be forgotten at a specified rate.

Simulation Method
---------------------

Currently, the simulation environment models a scenario in which
agents send information to each other. Originally, the network is
seeded with some initial set of information. Each agent has access to
some facts by having it in its inbox. Some of the information is
valuable and some of it is noise. The signal to noise ratio can be
changed.

The agents in the model are limited. They can only do one action at a
time (unless they explicitly have higher capacity). The main action
that is implemented in the simulation is sharing of information in
one's inbox. At each point in time, if the agent is willing for that
period, it can do one of two actions:

-  Send one piece of information that is in its outbox to a neighbor:
   from most trusted to the least trusted if trust is used, randomly
   otherwise.

-  Pop one piece of information that is in its inbox, determine if it
   is valuable, and then queue it to be sent to all neighbors by
   placing it in its outbox.

   When determining whether information is valuable or not, the
   competence of the agent determines how frequently the agent will
   get it correctly. 

   Then, the agent will decide who to send it to based on spamminess
   and selfishness parameters.

The simulation starts by processing all information that is in agents'
inbox and placing them in their outbox based on their
personalities. The agents are also seeded with initial trust if trust
is used. The simulation then proceeds for a predetermined number of
steps.

Periodically a set of performance statistics area collected from the
networked. These statistics are summarized at the end of the
simulation. Simulations can be repeated for a number of prespecified
times and the average performance is reported at the end. 

Performance statistics considered include:

-  **Situation awareness (SA)** is the average percentage of all valuable
   facts known to all the agents in the network. 

-  **Situation awareness single (SA-0)** is the average percentage of
   all  valuable facts known to a specific agent in the network. This
   helps us model the case where only a single agent getting the
   relevant information is important. Often agent 0 is monitored for
   this purpose. Agent 0 is also the lead of the group in the
   hierarchy graph.

-  **Communications** is the total number of messages sent in the
   network. Communications are monitored as a function of the number
   of messages needed to reach a certain level of SA (or SA-0).

-  **Steps** is the total number of simulation steps needed to reach a
   certain level of SA (or SA-0).

The simulation is implemented in the :mod:`simulation` module:

  https://github.com/rpitrust/agentsimulation/blob/master/simulation.py
