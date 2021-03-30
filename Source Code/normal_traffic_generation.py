#!/usr/bin/python
from scapy.all import *
from time import ctime,time
import random
import os

class Slave():
    def __init__(self, sock=None):
        print("normal mode loaded")

        # get ntp times
	ntp_res=time()

        
    def Pings(self):
        
	normal = input ("--------------------------------------\n"
				"Choose the type of normal trafic :\n"
				"1 for TCP  \n"
				"2 for UDP  \n" 
				"3 for ICMP \n"
			  "--------------------------------------\n"
				"Answer : ")
	x= int(normal)
	if x == 1:
		print ("|[TCP....!!!!] |")
		for i in range(10):
			bytes = random.randrange(5,10)
			size = random .randrange(512,1024)
			os.system("iperf -c 10.0.0.7 -p 5201 -b {}KB -l {}B -i 1 -t 20s".format(bytes,size))
	if x == 2:
		print ("|[UDP....!!!!] |")
		for i in range(10):
			bytes = random.randrange(5,10)
			size = random .randrange(512,1024)
			os.system("iperf -u -c 10.0.0.7 -p 5201 -b {}KB -l {}B -i 1 -t 20s".format(bytes,size))
	if x == 3:
		print ("|[ICMP....!!!!] |")
		for i in range(5,10):
			count = random.randrange(10,25)
			os.system("ping -c {} 10.0.0.{} -i 1".format(count,i))
		
        #ddos.close()
	print ("GENERATION FINISHED!!") 

if __name__ == '__main__':
  slaveNode = Slave()
  slaveNode.Pings()
