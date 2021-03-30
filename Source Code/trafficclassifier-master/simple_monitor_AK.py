import switch
from ryu.controller import ofp_event
from ryu.controller.handler import MAIN_DISPATCHER, DEAD_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.lib import hub
from ryu.lib.packet import in_proto
from operator import attrgetter
from datetime import datetime
import time

class CollectTrainingStatsApp(switch.SimpleSwitch13):

    def __init__(self, *args, **kwargs):
        super(CollectTrainingStatsApp, self).__init__(*args, **kwargs)
        self.datapaths = {}
        self.monitor_thread = hub.spawn(self._monitor)
        self.fields = {'time':'','datapath':'','ip_src':'','src_port':'','ip_dst':'','dst_port':'','protocol':'','total_packets':0,'total_bytes':0,'flow_duration':0,'idle_timeout':'','hard_timeout':''}

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
        self.logger.info('time\tdatapath\tip_src\tsrc_port\tip_dst\tdst_port\tprotocol\ttotal_packets\ttotal_bytes\tflow_duration\tidle_timeout\thard_timeout')
        while True:
            for dp in self.datapaths.values():
                self._request_stats(dp)
            hub.sleep(3)

    def _request_stats(self, datapath):
        self.logger.debug('send stats request: %016x', datapath.id)
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        req = parser.OFPFlowStatsRequest(datapath)
        datapath.send_msg(req)

        req = parser.OFPPortStatsRequest(datapath, 0, ofproto.OFPP_ANY)
        datapath.send_msg(req)

    @set_ev_cls(ofp_event.EventOFPFlowStatsReply, MAIN_DISPATCHER)
    def _flow_stats_reply_handler(self, ev):
        tp_src = 0
        tp_dst = 0
        proto = 0
        body = ev.msg.body

        for stat in sorted([flow for flow in body if flow.priority == 1],
                           key=lambda flow: (flow.match['eth_type'],flow.match['ipv4_src'],flow.match['ipv4_dst'],flow.match['ip_proto'])):
            
            ip_src = stat.match['ipv4_src']
            ip_dst = stat.match['ipv4_dst']
            ip_proto = stat.match['ip_proto']
            
            if stat.match['ip_proto'] == 1:
                proto = 3          

            elif stat.match['ip_proto'] == in_proto.IPPROTO_TCP:
                tp_src = stat.match['tcp_src']
                tp_dst = stat.match['tcp_dst']
                proto = 1

            elif stat.match['ip_proto'] == in_proto.IPPROTO_UDP:
                tp_src = stat.match['udp_src']
                tp_dst = stat.match['udp_dst']
                proto = 2

           
           
	    #print details of flows
	    current_milli_time = lambda: int(round(time.time() * 1000))
            timestamp= current_milli_time()
            self.fields['time'] = timestamp
            self.fields['datapath'] = ev.msg.datapath.id
            self.fields['ip_src'] = ip_src
            self.fields['src_port'] = tp_src
            self.fields['ip_dst'] = ip_dst
            self.fields['dst_port'] = tp_dst
            self.fields['protocol'] = proto
            self.fields['total_packets'] = stat.packet_count
            self.fields['total_bytes'] = stat.byte_count
            self.fields['flow_duration'] = stat.duration_sec
            self.fields['idle_timeout'] = stat.idle_timeout
            self.fields['hard_timeout'] = stat.hard_timeout
            self.logger.info('data\t%s\t%x\t%s\t%d\t%s\t%d\t%d\t%d\t%d\t%d\t%s\t%s',self.fields['time'],self.fields['datapath'],self.fields['ip_src'],
self.fields['src_port'],self.fields['ip_dst'],self.fields['dst_port'],self.fields['protocol'],self.fields['total_packets'],self.fields['total_bytes'],
self.fields['flow_duration'],self.fields['idle_timeout'],self.fields['hard_timeout'])
