
Overview of the Agent Simulation Package
=========================================

This package implements an agent scenario in which agents share
information with each other in a networked setting. The package
incorporates many adjustable parameters that are easily extensible. We
give an overview of these characteristics in this document.

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

The :mod:`GraphGen` module implements this function. 

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

