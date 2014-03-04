import SocketServer

#SimulationServer deals with any actual server issues
#Right now, it's only used to keep track of timeouts
class SimulationServer(SocketServer.TCPServer):

       #Timeout is 30 seconds
       timeout = 30
       alive = True

       def handle_timeout(self):
          print "Timed out"
          self.alive = False

       def isAlive(self):
          return self.alive

#SimulationHandler deals with handling server requests.
#It passes out new config files to slaves, and outputs their data
class SimulationHandler(SocketServer.BaseRequestHandler):

       config_list = ["test"]
       server_list = {}

       def handle(self):
          self.data = self.request.recv(8192)
          if self.data == "request": #Handle a request
              print "Request received from " + self.client_address[0]
              if self.config_list: #If there are config files remaining
                  print "Sending config file: " + self.config_list[0] + ".txt"
                  self.request.send(self.config_list[0] + ".txt") #Send the filename
                  f = open(self.config_list[0] + ".txt") #Send the text in the file
                  text = f.read(8192)
                  while(text):
                      self.request.send(text)
                      text = f.read(1024)
                  f.close
                  self.server_list[self.client_address[0]] = self.config_list[0]
                  del self.config_list[0]

              else: #No more config files remaining
                  print "Last config file sent."
                  
              self.request.send("done") #Send the finished signal
              
                  

          else: #If it's not a new request, then it's output
              print "Output packet received from " + self.client_address[0]
              f = open(self.server_list[self.client_address[0]] + "_output.txt","a")
              f.write( self.data )
              f.write("\n")
              f.close()
              print "Printing output to " + self.server_list[self.client_address[0]]


if __name__ == "__main__":
    server = SimulationServer(('',2436), SimulationHandler)
    print "starting server"
    while server.isAlive():
       server.handle_request()
