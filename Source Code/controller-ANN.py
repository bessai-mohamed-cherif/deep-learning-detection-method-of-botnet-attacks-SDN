from ryu.controller import ofp_event
from ryu.controller.handler import MAIN_DISPATCHER, DEAD_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.lib import hub
from ryu.lib.packet import in_proto
import Flux
import simple
import time 
import pandas as pd
import os
from tensorflow.keras.models import load_model


flux = {} #empty flow dictionary
class SimpleMonitor13(simple.SimpleSwitch13):

    def __init__(self, *args, **kwargs):

        super(SimpleMonitor13, self).__init__(*args, **kwargs)
        self.datapaths = {}
        self.monitor_thread = hub.spawn(self._monitor)
        self.flow_model = load_model('3final.h5')
        
        self.logger.info("------------------ Model loaded successfully... -----------------------")
        
    @set_ev_cls(ofp_event.EventOFPStateChange,
                [MAIN_DISPATCHER, DEAD_DISPATCHER])
    def _state_change_handler(self, ev):
        datapath = ev.datapath
        if ev.state == MAIN_DISPATCHER:
            if datapath.id not in self.datapaths:
                self.logger.debug('register datapath: %016x', datapath.id)
                self.datapaths[datapath.id] = datapath
        elif ev.state == DEAD_DISPATCHER:
            if datapath.id in self.datapaths:
                self.logger.debug('unregister datapath: %016x', datapath.id)
                del self.datapaths[datapath.id]

    def _monitor(self):
        
            j = 0
            while j < 10 : #5 minutes to stop the program after 10 tries
                file0 = open("PredictANN.csv","w")
                file0.write('dst2src_packets_rate,src2dst_packets_rate,dst2src_inter_time_std,dst2src_packets,src2dst_inter_time_std,src2dst_inter_time_max,flow_use_time,protocol,src2dst_packets,flow_duration,dst2src_inter_time_max,packets,src2dst_inter_time_avg,flow_idle_time,bytes,dst2src_inter_time_avg \n')
                file0.close()
                i = 0
                while i < 10:
                    for dp in self.datapaths.values():
                        self._request_stats(dp)
                    hub.sleep(3)
                    i = i + 1
                if j != 0 :    
                    self.flow_predict()
                j = j + 1
            
            print ("DETECTION COMPLETED")
            os._exit(1)
        
          

    def _request_stats(self, datapath):
        self.logger.debug('send stats request: %016x', datapath.id)
        parser = datapath.ofproto_parser

        req = parser.OFPFlowStatsRequest(datapath)
        datapath.send_msg(req)

    @set_ev_cls(ofp_event.EventOFPFlowStatsReply, MAIN_DISPATCHER)
    def _flow_stats_reply_handler(self, ev):


        #file0 = open("PredictANN.csv","w")
        #file0.write('dst2src_packets_rate,src2dst_packets_rate,dst2src_inter_time_std,dst2src_packets,src2dst_inter_time_std,src2dst_inter_time_max,flow_use_time,protocol,src2dst_packets,flow_duration,dst2src_inter_time_max,packets,src2dst_inter_time_avg,flow_idle_time,bytes,dst2src_inter_time_avg \n')
        file0 = open("PredictANN.csv","a+")
        
        body = ev.msg.body
        tp_src = 0
        tp_dst = 0

        for stat in sorted([flow for flow in body if (flow.priority == 1) ], key=lambda flow:
            (flow.match['eth_type'],flow.match['ipv4_src'],flow.match['ipv4_dst'],flow.match['ip_proto'])):
        
            ip_src = stat.match['ipv4_src']
            ip_dst = stat.match['ipv4_dst']
            current_milli_time = lambda: int(round(time.time() * 1000))
            timestamp= current_milli_time()
            #print(timestamp)
             
            if stat.match['ip_proto'] == 1:
                proto = 3

            elif stat.match['ip_proto'] == in_proto.IPPROTO_TCP:
                tp_src = stat.match['tcp_src']
                tp_dst = stat.match['tcp_dst']
                proto = 2

            elif stat.match['ip_proto'] == in_proto.IPPROTO_UDP:
                tp_src = stat.match['udp_src']
                tp_dst = stat.match['udp_dst']
                proto = 1
		 
            
            
            unique_id = hash(''.join([str(ev.msg.datapath.id),ip_src,str(tp_src),ip_dst,str(tp_dst)])) #create unique ID for flow based on switch ID, source host,and destination host
	       
            if unique_id in flux.keys():
                  flux[unique_id].updateforward(int(stat.packet_count),int(stat.byte_count),int(timestamp),int (stat.duration_sec)) #update forward attributes with time, packet, and byte count and duration
			
            else:
                  rev_unique_id = hash(''.join([str(ev.msg.datapath.id),ip_dst,str(tp_dst),ip_src,str(tp_src)])) #switch source and destination to generate same hash for src/dst and dst/src
                  if rev_unique_id in flux.keys():
                      flux[rev_unique_id].updatereverse(int(stat.packet_count),int(stat.byte_count),int(timestamp),int (stat.duration_sec)) #update reverse attributes with time, packet, and byte count and duration
                  else:
                      flux[unique_id] = Flux.Flux(int(timestamp),ev.msg.datapath.id, ip_src, tp_src, ip_dst, tp_dst, proto, stat.packet_count,stat.byte_count,int(stat.duration_sec),int(stat.idle_timeout),int(stat.hard_timeout)) #create new flow object
            
           
            #print("\nprinting to file the stats") 
	      
            for key,flow in flux.items():
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
                      file0.write(outstring+'\n')

        file0.close()
	    
        


    def flow_predict(self):
        
        try:
            predict_flow_dataset = pd.read_csv('PredictANN.csv')
            X_predict_flow = predict_flow_dataset.iloc[:, :].values
            
            y_flow_pred = self.flow_model.predict(X_predict_flow)
            y_flow_pred = (y_flow_pred > 0.5)

            legitimate_trafic = 0
            ddos_trafic = 0
	
            for i in y_flow_pred:
                if i == 0:
                    legitimate_trafic = legitimate_trafic + 1
                else:
                    ddos_trafic = ddos_trafic + 1
                    
            
            
            self.logger.info("------------------------------------------------------------------------------")
	   
            if (float(legitimate_trafic)/(legitimate_trafic+ddos_trafic)*100) >= 70.00:
                self.logger.info("\t\t\tNormal traffic detected ...")
                self.logger.info("\t\t\tAccuracy_score :{:.2f}%".format(float(legitimate_trafic)/(legitimate_trafic+ddos_trafic)*100))
		
            else:
                self.logger.info("\t\t\tWarning BOTNET activity detected ...")
                self.logger.info("\t\t\tAccuracy_score :{:.2f}%".format(float(ddos_trafic)/(legitimate_trafic+ddos_trafic)*100))

            self.logger.info("* total traffic :{0}".format(ddos_trafic+legitimate_trafic))
            self.logger.info("* normal traffic :{0}".format(legitimate_trafic))
            self.logger.info("* DDOS traffic :{0}".format(ddos_trafic))
            
	    
            self.logger.info("------------------------------------------------------------------------------")


            
        except Exception as e:
            if not str(e).startswith("\'bool\'"):
            
                print (e)

                pass   

        
