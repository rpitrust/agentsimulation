import socket
import runner
import os
import sys

#Set this to the local IP of the master process
HOST = '192.168.17.108'
PORT = 2436

if __name__ == '__main__':

    done = False

    if len(sys.argv) > 1:
        HOST = sys.argv[1]

    #Continue our loop until the master is no longer sending files
    while not done:
        #Request a file
        print "Requesting new config file\n"
        sock = socket.socket()
        sock.connect((HOST,PORT))
        sock.sendall("request.")
        config_file = sock.recv(4)

        #No files remaining, time to finish
        if config_file == "done":
            print "All config files complete. Shutting down."
            done = True

        #A new file has been sent. Copy it locally, then run it.
        else:
            config_file = sock.recv(int(config_file)) #Get the name of the file
            print "Running config file: " + config_file
            f = open(config_file,"w")
            data = sock.recv(8) #Get the data
            data = sock.recv(int(data))
            f.write(data)
            f.close()
            sock.close()
            runner.run(config_file, HOST, True) #Run it
            os.remove(config_file) #Clean up
            sock = socket.socket()
            sock.connect((HOST,PORT))
            sock.send("complete") #We finished the file, tell the server