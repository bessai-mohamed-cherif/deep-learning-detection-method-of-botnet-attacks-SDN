#!/usr/bin/python
import subprocess, sys #to handle the Ryu output
import signal #for timer
import os #for process handling
import numpy as np #for model features
import math
## command to run ##
cmd = "ryu-manager simple_monitor_AK.py"
flows = {} #empty flow dictionary
TIMEOUT = 3*60 #2 min #how long to collect training data
class Flow:
    def __init__(self, time_start,datapath,ip_src,src_port,ip_dst,dst_port,protocol,total_packets,total_bytes,flow_duration,idle_timeout,hard_timeout):
        self.time_start = time_start
        self.datapath = datapath
        self.ip_src = ip_src
        self.src_port = src_port
        self.ip_dst = ip_dst
        self.dst_port = dst_port
        self.protocol = protocol
        self.duration = flow_duration
        self.idle_timeout = idle_timeout
        self.hard_timeout = hard_timeout
	
        self.total_packet = 0
        self.total_byte = 0
        
        self.i = 0
        
        
        #attributes for forward flow direction (source -> destination)
        self.forward_packets = total_packets
        self.forward_bytes = total_bytes
        self.forward_delta_packets = 0
        #self.forward_delta_bytes = 0
        self.forward_inst_inter_time = 0.00
        self.forward_inter_time_std = 0.00
        self.forward_inter_time_max = 0.00
        self.forward_inter_time_min = 0.00
        self.forward_avg_pps = 0.00
        self.forward_avg_bps = 0.00
        self.forward_inter_time_avg = 0.00
        self.forward_last_time = time_start
	
        
        #attributes for reverse flow direction (destination -> source)
        self.reverse_packets = 0
        self.reverse_bytes = 0
        self.reverse_delta_packets = 0
        #self.reverse_delta_bytes = 0
        self.reverse_inst_inter_time = 0.00
        self.reverse_inter_time_std = 0.00
        self.reverse_inter_time_max = 0.00
        self.reverse_inter_time_min = 0.00
        self.reverse_avg_pps = 0.00
        self.reverse_avg_bps = 0.00
        self.reverse_inter_time_avg = 0.00
        self.reverse_last_time = time_start
        
    #updates the attributes in the forward flow direction
    def updateforward(self, packets, bytes, curr_time,duration):
       
        self.forward_delta_packets = packets - self.forward_packets
        self.forward_packets = packets
        
        if curr_time != self.time_start: self.forward_avg_pps = packets/float(curr_time-self.time_start)
        
        
        #self.forward_delta_bytes = bytes - self.forward_bytes
        self.forward_bytes = bytes
        if curr_time != self.time_start: self.forward_avg_bps = bytes/float(curr_time-self.time_start)
        
        try:
            if curr_time != self.forward_last_time: self.forward_inst_inter_time = float(curr_time-self.forward_last_time) /self.forward_delta_packets
	    
        except:
            self.forward_inst_inter_time=0
            
        if self.i == 0: 
                self.forward_inter_time_max = self.forward_inst_inter_time
                self.forward_inter_time_min = self.forward_inst_inter_time
                self.i = +1
                
                
        else :
                if self.forward_inter_time_max <= self.forward_inst_inter_time : self.forward_inter_time_max = self.forward_inst_inter_time
                if self.forward_inter_time_min > self.forward_inst_inter_time : self.forward_inter_time_min = self.forward_inst_inter_time           

        self.forward_inter_time_std= math.sqrt(math.pow(self.forward_inter_time_avg - self.forward_inst_inter_time,2))
        self.forward_last_time = curr_time
        self.duration = duration
        self.total_packet = self.forward_packets + self.reverse_packets
        self.total_byte = self.forward_bytes + self.reverse_bytes
        try:
            	self.forward_inter_time_avg = self.duration/self.forward_packets
        except:
             self.forward_inter_time_avg=0

    #updates the attributes in the reverse flow direction
    def updatereverse(self, packets, bytes, curr_time,duration):
        self.reverse_delta_packets = packets - self.reverse_packets
        self.reverse_packets = packets
        
        if curr_time != self.time_start: self.reverse_avg_pps = packets/float(curr_time-self.time_start)

	#self.reverse_delta_bytes = bytes - self.reverse_bytes
        self.reverse_bytes = bytes
        if curr_time != self.time_start: self.reverse_avg_bps = bytes/float(curr_time-self.time_start)

        try:
            if curr_time != self.reverse_last_time: self.reverse_inst_inter_time = float(curr_time-self.reverse_last_time)/self.reverse_delta_packets
        except:
            self.reverse_inst_inter_time=0

        
        
        self.reverse_inter_time_std= math.sqrt(math.pow(self.forward_inter_time_avg - self.forward_inst_inter_time,2))
        self.reverse_last_time = curr_time
        self.duration = duration
        
        self.total_packet = self.forward_packets + self.reverse_packets
        self.total_byte = self.forward_bytes + self.reverse_bytes
        try:
            	self.reverse_inter_time_avg = self.duration/self.reverse_packets
        except:
             self.reverse_inter_time_avg = 0



    

#for timer to collect flow training data
def alarm_handler(signum, frame):
    print("Finished collecting data.")
    raise Exception()
        
def run_ryu(p,f=None):
    ## run it ##
    
    while True:
       
        print ('going through loop')

        out = p.stderr
        for line in out :
          print (line)
          if line == '' and p.poll() != None:
              break
          if line != '' and line.startswith(b'data'): #when Ryu 'simple_monitor_AK.py' script returns output
              fields = line.split(b'\t')[1:] #split the flow details
            
              fields = [f.decode(encoding='utf-8', errors='strict') for f in fields] #decode flow details 
	    
            
              unique_id = hash(''.join([fields[1],fields[2],fields[4]])) #create unique ID for flow based on switch ID, source host,and destination host
       
              if unique_id in flows.keys():
                  flows[unique_id].updateforward(int(fields[7]),int(fields[8]),int(fields[0]),int (fields[9])) #update forward attributes with time, packet, and byte count and duration
			
              else:
                  rev_unique_id = hash(''.join([fields[1],fields[4],fields[2]])) #switch source and destination to generate same hash for src/dst and dst/src
                  if rev_unique_id in flows.keys():
                      flows[rev_unique_id].updatereverse(int(fields[7]),int(fields[8]),int(fields[0]),int (fields[9])) #update reverse attributes with time, packet, and byte count and duration
                  else:
                      flows[unique_id] = Flow(int(fields[0]), fields[1], fields[2], fields[3], fields[4], fields[5], int(fields[6]), int(fields[7]),int(fields[8]),int(fields[9]),int(fields[10]),int(fields[11])) #create new flow object
           
              print("\nprinting to file the stats") 
              for key,flow in flows.items():
                  x1 = int(round(flow.forward_avg_pps))
                  x2 = int(round(flow.forward_avg_bps))
                  x3 = int(round(flow.reverse_avg_pps))
                  x4 = int(round(flow.reverse_avg_bps))
                  outstring = ','.join([
		flow.ip_src,flow.ip_dst,
    		str(flow.protocol),
    		str(flow.forward_packets),
    		str(flow.forward_bytes),
        	str(x1),
        	str(x2), 
        	str(flow.reverse_packets),
        	str(flow.reverse_bytes),
        	str(x3),
        	str(x4),
		str(flow.total_packet),str(flow.total_byte),
		str(int(flow.duration*1000)),"0",
		str(int(flow.forward_inter_time_avg*1000)),
		str(int(flow.reverse_inter_time_avg*1000)),"0",
		str(int(flow.idle_timeout*1000)),
		str(int(flow.hard_timeout*1000)),
		str(int(flow.forward_inter_time_std*1000)),
		str(int(flow.reverse_inter_time_std*1000)),
		str(int(flow.forward_inter_time_max*1000)),
		str(int(flow.forward_inter_time_min*1000))])
                  f.write(outstring+'\n')
        p.stderr.close()
              
	       

if __name__ == '__main__':
   

   
    
    p = subprocess.Popen(cmd, shell=True, stderr=subprocess.PIPE) #start Ryu process
    signal.signal(signal.SIGALRM, alarm_handler) #start signal process
    signal.alarm(TIMEOUT) #set for 2 minutes
    f = open('training_data.csv', 'w') #open training data output file
                
    try:
        headers = 'ip_src,ip_dst,protocol,src2dst packets,src2dst Bytes,src2dst Packet rate,src2dst Byte rate,dst2src Packets,dst2src Bytes,dst2src Packet rate, dst2src Byte rate,packets,bytes,flow duration(ms),src2dst_inter_time_min,src2dst_inter_time_avg,dst2src_inter_time_avg,inter_time_min,idle_timeout,hard_timeout,src2dst_inter_time_std,dst2src_inter_time_std,src2dst_inter_time_max,src2dst_inter_time_min\n'

        f.write(headers)
        run_ryu(p,f=f)
       

    except Exception as e:
        print(e)
        os.killpg(os.getpgid(p.pid), signal.SIGTERM) #kill ryu process on exit
        f.close()
           
    
