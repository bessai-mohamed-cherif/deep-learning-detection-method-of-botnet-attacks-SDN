import math
class Flux:
    def __init__(self,	time_start,datapath,ip_src,src_port,ip_dst,dst_port,protocol,total_packets,total_bytes,flow_duration,idle_timeout,hard_timeout):
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
        self.use_time = 0.00
        
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
            self.forward_inst_inter_time = float(curr_time-self.forward_last_time) /self.forward_delta_packets
            if (self.forward_inst_inter_time < 0) : self.forward_inst_inter_time = 0
	    
        except:
            self.forward_inst_inter_time=0
        

        try:
            	self.forward_inter_time_avg = float(curr_time-self.time_start)/self.forward_packets
        except:
             	self.forward_inter_time_avg = 0
        
            
        if self.i == 0: 
                self.forward_inter_time_max = self.forward_inst_inter_time
                self.forward_inter_time_min = self.forward_inst_inter_time
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
           self.reverse_inst_inter_time = float(curr_time-self.reverse_last_time)/self.reverse_delta_packets
           if (self.reverse_inst_inter_time < 0) : self.reverse_inst_inter_time = 0
        except:
            self.reverse_inst_inter_time =0
            
        
        try:
            	self.reverse_inter_time_avg = float(curr_time-self.time_start)/self.reverse_packets

        except:
             	self.reverse_inter_time_avg = 0

        if self.i == 0: 
                self.reverse_inter_time_max = self.reverse_inst_inter_time
                self.reverse_inter_time_min = self.reverse_inst_inter_time
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
	

   
