#!/usr/bin/python
import subprocess #to handle the Ryu output
import signal #for timer
import os #for process handling
import math
import pandas as pd
import time
from tensorflow.keras.models import load_model
## command to run ##
cmd = "ryu-manager ~/flowmanager/flowmanager.py simple_monitor_AK.py"
flows = {} #empty flow dictionary
TIMEOUT = 20 #20 seconds #how long to collect training data

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
        self.use_time = 0
        
	
        
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
        try:
        	if curr_time != self.time_start: self.forward_avg_pps = packets/float((curr_time-self.time_start)/1000)
        except:
            self.forward_avg_pps=0
	#if curr_time != self.time_start: self.forward_avg_pps = packets/duration
        
        
        #self.forward_delta_bytes = bytes - self.forward_bytes
        
	#if curr_time != self.time_start: self.forward_avg_bps = bytes/duration
        
        
        

        try:
            	self.forward_inter_time_avg = float(curr_time-self.time_start)/self.forward_packets
        except:
             	self.forward_inter_time_avg = 0
        try:
            self.forward_inst_inter_time = float(curr_time-self.forward_last_time) /self.forward_delta_packets
            if (self.forward_inst_inter_time < 0) : self.forward_inst_inter_time = 0
            
	    
        except:
            self.forward_inst_inter_time=0
        
            
        if self.i == 0: 
                self.forward_inter_time_max = self.forward_inter_time_avg
                self.forward_inter_time_min = self.forward_inter_time_avg
                self.i = +1
                
	
                
        else :
                if self.forward_inter_time_max <= self.forward_inst_inter_time : self.forward_inter_time_max = self.forward_inst_inter_time
                if self.forward_inter_time_min > self.forward_inst_inter_time : self.forward_inter_time_min = self.forward_inst_inter_time           

        self.forward_inter_time_std= math.sqrt(math.pow(self.forward_inter_time_avg - self.forward_inst_inter_time,2))
        self.forward_last_time = curr_time
        self.use_time = self.use_time + self.forward_inst_inter_time
        self.duration = duration
        self.total_packet = self.forward_packets + self.reverse_packets
        self.total_byte = self.forward_bytes + self.reverse_bytes

    #updates the attributes in the reverse flow direction
    def updatereverse(self, packets, bytes, curr_time,duration):
        self.reverse_delta_packets = packets - self.reverse_packets
        self.reverse_packets = packets
        try:
        	if curr_time != self.time_start: self.reverse_avg_pps = packets/float((curr_time-self.time_start)/1000)
        except:
            self.reverse_avg_pps = 0
	#self.reverse_delta_bytes = bytes - self.reverse_bytes
        

        
        
        try:
            	self.reverse_inter_time_avg = float(curr_time-self.time_start)/self.reverse_packets

        except:
             	self.reverse_inter_time_avg = 0
        try:
           self.reverse_inst_inter_time = float(curr_time-self.reverse_last_time)/self.reverse_delta_packets
           if (self.reverse_inst_inter_time < 0) : self.reverse_inst_inter_time = 0
          
        except:
            self.reverse_inst_inter_time =0
            


        if self.i == 0: 
                self.reverse_inter_time_max = self.reverse_inter_time_avg
                self.reverse_inter_time_min = self.reverse_inter_time_avg
                self.i = +1
                
                
        else :
                if self.reverse_inter_time_max <= self.reverse_inst_inter_time : self.reverse_inter_time_max = self.reverse_inst_inter_time
                if self.reverse_inter_time_min > self.reverse_inst_inter_time : self.reverse_inter_time_min = self.reverse_inst_inter_time
        
        self.reverse_inter_time_std= math.sqrt(math.pow(self.forward_inter_time_avg - self.forward_inst_inter_time,2))
        self.use_time = self.use_time + self.reverse_inst_inter_time        
        self.reverse_last_time = curr_time
        self.duration = duration
        
        self.total_packet = self.forward_packets + self.reverse_packets
        self.total_byte = self.forward_bytes + self.reverse_bytes
        



    

#for timer to collect flow training data
def alarm_handler(signum, frame):
    print("Finished collecting data.")
    
    raise Exception()
        
def run_ryu(p,f=None):
    ## run it ##
    
    while True:
       
        

        out = p.stderr
        for line in out :
          print (line)
          if line == '' and p.poll() != None:
              break
          if line != '' and line.startswith(b'data'): #when Ryu 'simple_monitor_AK.py' script returns output
              fields = line.split(b'\t')[1:] #split the flow details
            
              fields = [f.decode(encoding='utf-8', errors='strict') for f in fields] #decode flow details 
	    
            
              unique_id = hash(''.join([fields[1],fields[2],fields[3],fields[4],fields[5]])) #create unique ID for flow based on switch ID, source host,and destination host
       
              if unique_id in flows.keys():
                  flows[unique_id].updateforward(int(fields[7]),int(fields[8]),int(fields[0]),int (fields[9])) #update forward attributes with time, packet, and byte count and duration
			
              else:
                  rev_unique_id = hash(''.join([fields[1],fields[4],fields[5],fields[2],fields[3]])) #switch source and destination to generate same hash for src/dst and dst/src
                  if rev_unique_id in flows.keys():
                      flows[rev_unique_id].updatereverse(int(fields[7]),int(fields[8]),int(fields[0]),int (fields[9])) #update reverse attributes with time, packet, and byte count and duration
                  else:
                      flows[unique_id] = Flow(int(fields[0]), fields[1], fields[2], fields[3], fields[4], fields[5], int(fields[6]), int(fields[7]),int(fields[8]),int(fields[9]),int(fields[10]),int(fields[11])) #create new flow object
           
              print("\nprinting to dataset the stats") 
	      
              for key,flow in flows.items():
                  x1 = int(round(flow.forward_avg_pps))
                  #x2 = int(round(flow.forward_avg_bps))
                  x3 = int(round(flow.reverse_avg_pps))
                  #x4 = int(round(flow.reverse_avg_bps))
                  if(flow.duration*1000-flow.use_time > 0):
                      x5 = flow.duration*1000-flow.use_time
                  else:
                      x5 = 0
                  if (flow.total_packet !=0 or flow.total_byte !=0):
                      	outstring = ','.join([
                     	str(x3),str(x1),
                     	str(int(flow.reverse_inter_time_std)),
                     	str(flow.reverse_packets),
                     	str(int(flow.forward_inter_time_std)),
	 	     	    str(int(flow.forward_inter_time_max)),
                     	str(int(flow.use_time)),
                     	str(flow.protocol),
                     	str(flow.forward_packets),
                     	str(int(flow.duration*1000)),
                     	str(int(flow.reverse_inter_time_max)),
                     	str(flow.total_packet),
                     	str(int(flow.forward_inter_time_avg)),
                     	str(int(x5)),
                     	str(flow.total_byte),
                     	str(int(flow.reverse_inter_time_avg))
                     	])
                      	f.write(outstring+'\n')
        p.stderr.close()
              
def flow_predict():
        
        try:
            predict_flow_dataset = pd.read_csv('training_data.csv')
            X_predict_flow = predict_flow_dataset.iloc[:, :].values
            flow_model = load_model('3layers.h5')
            print("model loaded")
            y_flow_pred = flow_model.predict(X_predict_flow)
            y_flow_pred = (y_flow_pred > 0.5)

            legitimate_trafic = 0
            ddos_trafic = 0
	
            for i in y_flow_pred:
                if i == 0:
                    legitimate_trafic = legitimate_trafic + 1
                else:
                    ddos_trafic = ddos_trafic + 1
                    
            
            print("------------------------------------------------------------------------------")
	   
            if (float(legitimate_trafic)/(legitimate_trafic+ddos_trafic)*100) >= 50.00:
                print("\t\t\tNormal traffic detected ...")
                print("\t\t\taccuracy_score :{:.2f}%".format(float(legitimate_trafic)/(legitimate_trafic+ddos_trafic)*100))
		
            else:
                print("\t\t\tWarning BOTNET activity detected ...")
                print("\t\t\taccuracy_score :{:.2f}%".format(float(ddos_trafic)/(legitimate_trafic+ddos_trafic)*100))

            print("* total traffic :{0}".format(ddos_trafic+legitimate_trafic))
            print("* normal traffic :{0}".format(legitimate_trafic))
            print("* botnet traffic :{0}".format(ddos_trafic))
            
	    
            print("------------------------------------------------------------------------------")


            
        except Exception as e:
	    
            if(not str(e).startswith("\'bool\'")):
                print (e)
                pass   
	       

if __name__ == '__main__':
   

    i=0
    p = subprocess.Popen(cmd, shell=True, stderr=subprocess.PIPE) #start Ryu process
    while i <= 5:
	    
	    signal.signal(signal.SIGALRM, alarm_handler) #start signal process
	    signal.alarm(TIMEOUT) #set for 2 minutes
	    f = open('training_data.csv', 'w') #open training data output file
		        
	    try:
                headers = 'dst2src_packets_rate,src2dst_packets_rate,dst2src_inter_time_std,dst2src_packets,src2dst_inter_time_std,src2dst_inter_time_max,flow_use_time,protocol,src2dst_packets,flow_duration,dst2src_inter_time_max,packets,src2dst_inter_time_avg,flow_idle_time,bytes,dst2src_inter_time_avg \n'
                f.write(headers)
                time.sleep(5)
                
                run_ryu(p,f=f)
	       

	    except Exception as e:
                if i!=0 :
                    print(e)
                    flow_predict()
                f.close()
	    i = i + 1

    os.killpg(os.getpgid(p.pid), signal.SIGTERM) #kill ryu process on exit
        
        
           
    
