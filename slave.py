import socket
import runner

#REMINDER
#This will overwrite files on master machine
#Find out how to handle that situation
#For testing purposes, we're just dealing with 

#Set this to the local IP of the master process
HOST = '192.168.17.108'
PORT = 2436

if __name__ == '__main__':

    done = False

    #Continue our loop until the master is no longer sending files
    while not done:
        #Request a file
        print "Requesting new config file\n"
        sock = socket.socket()
        sock.connect((HOST,PORT))
        sock.sendall("request")
        config_file = sock.recv(1024)

        #No files remaining, time to finish
        if config_file == "done":
            print "All config files complete. Shutting down."
            done = True

        #A new file has been sent. Copy it locally, then run it.
        else:
            print "Running config file: " + config_file
#            f = open(config_file,"w")
            f = open("test2.txt","w")
            data = sock.recv(8192)
            while not data == "done": #Copy the file
                f.write(data)
                data = sock.recv(8192)
            f.close()
            runner.run(config_file, HOST, True) #Run it
