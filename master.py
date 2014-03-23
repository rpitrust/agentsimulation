import SocketServer
import sys
import os

config_dir = ""
output_dir = ""
output_sfx = "_output.txt"
incomplete_sfx = "_incomplete.txt"

#SimulationServer deals with any actual server issues
#Right now, it's only used to keep track of timeouts
class SimulationServer(SocketServer.TCPServer):

       #Timeout is 5 minutes
       timeout = 300
       alive = True

       def handle_timeout(self):
          print "Timed out"
          self.alive = False

       def isAlive(self):
          return self.alive

#SimulationHandler deals with handling server requests.
#It passes out new config files to slaves, and outputs their data
class SimulationHandler(SocketServer.BaseRequestHandler):

       server_list = {}

       #Gets the next unstarted config file. Returns an empty string if there are none remaining.
       def get_config(self):
          for config_file in os.listdir(config_dir + "/"): #Take a look at each file in our config directory
              config_file = config_file[:-4] #Strip off extension
              match = False #Check to see if it's in progress
              for in_progress in self.server_list.values():
                 if config_file == in_progress:
                    match = True
                    break
              if not os.path.isfile(os.path.join(output_dir + "/",config_file + output_sfx)) and not match: #If it's not complete and not in progress, we can start it
                 return config_file
              
          return ""

       def handle(self):
          self.data = self.request.recv(8192)
          if self.data == "request": #Handle a request
              print "Request received from " + self.client_address[0]
              config = self.get_config()
              if config: #If there are config files remaining
                  print "Sending config file: " + config + ".txt"
                  self.request.send(config + ".txt") #Send the filename
                  f = open(config_dir + "/" + config + ".txt") #Send the text in the file
                  text = f.read(1024)
                  while(text):
                      self.request.send(text)
                      text = f.read(1024)
                  self.request.close()
                  f.close
                  self.server_list[self.client_address[0]] = config

              else: #No more config files remaining
                  print "Last config file sent."                  
                  self.request.send("done")
              
          elif self.data == "complete": #If the job is done, rename the file and remove it from our in progress list
              config = self.server_list[self.client_address[0]]
              print "Completing file " + config + " on client " + self.client_address[0]
              os.rename(output_dir + "/" + config + incomplete_sfx, output_dir + "/" + config + output_sfx)
              del self.server_list[self.client_address[0]]

          else: #If it's not a recognized command, then it's output
              print "Output packet received from " + self.client_address[0]
              f = open(output_dir + "/" + self.server_list[self.client_address[0]] + incomplete_sfx,"a")
              f.write( self.data )
              f.write("\n")
              f.close()
              print "Printing output to " + self.server_list[self.client_address[0]]


#This deals with creating our output directory if necessary, and clearing it of incomplete files
def init_output():
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
    server = SimulationServer(('',2436), SimulationHandler)
    print "starting server"
    while server.isAlive():
       server.handle_request()
