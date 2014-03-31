"""
    The master requires folders for input configuration and output
    --see template for an example, and an output file for the results.
    Example:   python master.py config_dir output_dir
"""


import SocketServer
import sys
import os
from time import time

config_dir = ""
output_dir = ""
output_sfx = "_output.txt"
incomplete_sfx = "_incomplete.txt"
timeout = 1800

class SimulationHandler(SocketServer.BaseRequestHandler):
       """
       SimulationHandler deals with handling server requests.
       It passes out new config files to slaves, and outputs their data
       """

       server_list = {}
       timer_list = {}

       def get_config(self):
          for config_file in os.listdir(config_dir + "/"): #Take a look at each file in our config directory
              config_file = config_file[:-4] #Strip off extension
              match = False #Check to see if it's in progress
              for in_progress in self.server_list.values():
                 if config_file == in_progress:
                    match = True
                    break
              if not os.path.isfile(os.path.join(output_dir,config_file + output_sfx)) and not match: #If it's not complete and not in progress, we can start it
                 return config_file
                 
          #If there are no files remaining, see if there are any with expired timeouts
          if not self.server_list: return ""
          identity = min(self.timer_list, key=self.timer_list.get)
          if time() - self.timer_list[identity] > timeout:
              config_file = self.server_list[identity]
              os.remove(output_dir + "/" + config_file + incomplete_sfx)
              del self.server_list[identity]
              del self.timer_list[identity]
              return config_file
              
          return ""

       def handle(self):
          identity = self.request.recv(16)
          self.data = self.request.recv(8)
          if self.data == "request.": #Handle a request
              print "Request received from " + self.client_address[0] + " thread: " + identity
              config = self.get_config()
              if config: #If there are config files remaining
                  print "Sending config file: " + config + ".txt"
                  self.request.sendall('{0:0>4}'.format(str(len(config + ".txt")))) #Send the size of the filename
                  self.request.sendall(config + ".txt") #Send the filename
                  f = open(config_dir + "/" + config + ".txt") #Send the text in the file
                  text = f.read()
                  self.request.sendall('{0:0>8}'.format(str(len(text))))
                  self.request.sendall(text)
                  f.close
                  self.server_list[identity] = config
                  self.timer_list[identity] = time()

              else: #No more config files remaining
                  print "Last config file sent."                  
                  self.request.sendall("done")
              
          elif self.data == "complete": #If the job is done, rename the file and remove it from our in progress list
              config = self.server_list[identity]
              print "Completing file " + config + " on client " + self.client_address[0] + " thread: " + identity
              os.rename(output_dir + "/" + config + incomplete_sfx, output_dir + "/" + config + output_sfx)
              del self.server_list[identity]
              del self.timer_list[identity]

          elif self.data == "output..": #If it's output, get the size of the output then the output itself
              self.data = self.request.recv(8)
              self.data = self.request.recv(int(self.data))
              print "Output packet received from " + self.client_address[0] + " thread: " + identity
              self.timer_list[identity] = time()
              f = open(output_dir + "/" + self.server_list[identity] + incomplete_sfx,"a")
              f.write( self.data )
              f.write("\n")
              f.close()
              print "Printing output to " + self.server_list[identity] + incomplete_sfx
              
          else:
              print "Error: Unknown command '" + self.data + "' from " + self.client_address[0] + " thread: " + identity


def init_output():
    """
    init_output deals with creating our output directory if necessary, and clearing it of incomplete files
    """
    
    if not os.path.exists(output_dir): #Create directory
       os.mkdir(output_dir)
    for output_file in os.listdir(output_dir + "/"): #Remove incomplete output files
       if output_file.endswith(incomplete_sfx):
          os.remove(output_dir + "/" + output_file)
     

if __name__ == "__main__":
    if len(sys.argv) < 3:
       print "Usage: python master.py config_dir output_dir"
       sys.exit()

    config_dir = sys.argv[1]
    output_dir = sys.argv[2]
    init_output()
    server = SocketServer.TCPServer(('',2436), SimulationHandler)
    print "starting server"
    server.serve_forever()