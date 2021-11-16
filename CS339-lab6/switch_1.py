from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.lib.packet import packet, arp, ipv6, ethernet, ether_types
from ryu.lib import mac
import networkx as nx
from ryu.topology import event
from ryu.topology.api import get_switch, get_link
import matplotlib.pyplot as plt
import time


class SimpleSwitch13(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(SimpleSwitch13, self).__init__(*args, **kwargs)
        self.G = nx.DiGraph()
        self.topology_api_app = self
        self.arp_in = {}
        self.arp_table = {}
        self.last_switch = 0
        self.last_switch_time = 0

    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        datapath = ev.msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        match = parser.OFPMatch()
        actions = [parser.OFPActionOutput(ofproto.OFPP_CONTROLLER,
                                          ofproto.OFPCML_NO_BUFFER)]
        self.add_flow(datapath, 0, match, actions, 0)

    def add_flow(self, datapath, priority, match, actions, timeout=0):
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS,
                                             actions)]
        if timeout == 0:
            mod = parser.OFPFlowMod(datapath=datapath, priority=priority,
                                    match=match, instructions=inst)
        else:
            mod = parser.OFPFlowMod(datapath=datapath, priority=priority,
                                    match=match, instructions=inst, hard_timeout=timeout)
        datapath.send_msg(mod)

    @set_ev_cls(event.EventSwitchEnter, [CONFIG_DISPATCHER, MAIN_DISPATCHER])
    def get_topo(self, ev):
        switch_list = get_switch(self.topology_api_app)
        switches = [switch.dp.id for switch in switch_list]
        self.G.add_nodes_from(switches)

        link_list = get_link(self.topology_api_app)
        links = [(link.src.dpid, link.dst.dpid, {'attr_dict': {'port': link.src.port_no}}) for link in link_list]
        self.G.add_edges_from(links)
        links = [(link.dst.dpid, link.src.dpid, {'attr_dict': {'port': link.dst.port_no}}) for link in link_list]
        self.G.add_edges_from(links)
        # nx.draw(self.G)
        # plt.show()

    def get_out_port(self, datapath, src, dst, in_port):
        dpid = datapath.id

        # 开始时，各个主机可能在图中不存在，因为开始ryu只获取了交换机的dpid，并不知道各主机的信息，
        # 所以需要将主机存入图中
        if src not in self.G:
            self.G.add_node(src)
            self.G.add_edge(dpid, src, attr_dict={'port': in_port})
            self.G.add_edge(src, dpid)

        if dst in self.G:
            current_time = time.time()
            paths = list(nx.all_simple_paths(self.G, src, dst))
            path = []
            print('time', current_time-self.last_switch_time)
            if (current_time-self.last_switch_time) > 3:
                for p in paths:
                    if p[2] != self.last_switch:
                        path = p
                        self.last_switch = path[2]
                        self.last_switch_time = current_time
                        break
            else:
                for p in paths:
                    if p[2] == self.last_switch:
                        path = p
                        break
            print('datapath', dpid, 'path', path)
            next_hop = path[path.index(dpid) + 1]
            out_port = self.G[dpid][next_hop]['attr_dict']['port']
        else:
            out_port = datapath.ofproto.OFPP_FLOOD
        return out_port

    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def packet_in_handler(self, ev):
        msg = ev.msg
        datapath = msg.datapath
        ofp = datapath.ofproto
        ofp_parser = datapath.ofproto_parser

        dpid = format(datapath.id, "d").zfill(16)
        in_port = msg.match['in_port']

        pkt = packet.Packet(msg.data)
        eth = pkt.get_protocols(ethernet.ethernet)[0]
        if eth.ethertype == ether_types.ETH_TYPE_LLDP:
            # ignore lldp packet
            return
        dst = eth.dst
        src = eth.src
        data = msg.data
        self.logger.debug("packet in %s %s %s %s", dpid, src, dst, in_port)

        if pkt.get_protocol(ipv6.ipv6):  # drop the ipv6 packets
            match = ofp_parser.OFPMatch(eth_type=eth.ethertype)
            actions = []
            self.add_flow(datapath, 1, match, actions)
            return None

        arp_pkt = pkt.get_protocol(arp.arp)
        if arp_pkt:
            self.arp_table[arp_pkt.src_ip] = src  # ARP learning
            self.logger.info(" ARP: %s -> %s", arp_pkt.src_ip, arp_pkt.dst_ip)
            if self.arp_handler(msg):  # answer or drop
                return None
        out_port = self.get_out_port(datapath, src, dst, in_port)
        actions = [ofp_parser.OFPActionOutput(out_port)]

        # 如果执行的动作不是flood，那么此时应该依据流表项进行转发操作，所以需要添加流表到交换机
        if out_port != ofp.OFPP_FLOOD:
            match = ofp_parser.OFPMatch(in_port=in_port, eth_dst=dst, eth_src=src)
            self.add_flow(datapath=datapath, priority=1, match=match, actions=actions, timeout=5)
        # 控制器指导执行的命令
        out = ofp_parser.OFPPacketOut(datapath=datapath, buffer_id=msg.buffer_id,
                                      in_port=in_port, actions=actions, data=data)
        datapath.send_msg(out)

    def arp_handler(self, msg):
        datapath = msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        in_port = msg.match['in_port']

        pkt = packet.Packet(msg.data)
        eth = pkt.get_protocols(ethernet.ethernet)[0]
        arp_pkt = pkt.get_protocol(arp.arp)

        if eth:
            eth_dst = eth.dst
            eth_src = eth.src

        if eth_dst == mac.BROADCAST_STR:  # and arp_pkt
            arp_dst_ip = arp_pkt.dst_ip
            arp_src_ip = arp_pkt.src_ip

            if (datapath.id, arp_src_ip, arp_dst_ip) in self.arp_in:
                # packet come back at different port.
                if self.arp_in[(datapath.id, arp_src_ip, arp_dst_ip)] != in_port:
                    datapath.send_packet_out(in_port=in_port, actions=[])
                    return True
            else:
                self.arp_in[(datapath.id, arp_src_ip, arp_dst_ip)] = in_port
                print(self.arp_in)

        if arp_pkt:
            opcode = arp_pkt.opcode
            if opcode == arp.ARP_REQUEST:
                arp_src_ip = arp_pkt.src_ip
                arp_dst_ip = arp_pkt.dst_ip

                if arp_dst_ip in self.arp_table:  # arp reply
                    actions = [parser.OFPActionOutput(in_port)]
                    ARP_Reply = packet.Packet()
                    ARP_Reply.add_protocol(ethernet.ethernet(ethertype=eth.ethertype,
                                                             dst=eth.src,
                                                             src=self.arp_table[arp_dst_ip]))
                    ARP_Reply.add_protocol(arp.arp(opcode=arp.ARP_REPLY,
                                                   src_mac=self.arp_table[arp_dst_ip],
                                                   src_ip=arp_dst_ip,
                                                   dst_mac=eth_src, dst_ip=arp_src_ip))

                    ARP_Reply.serialize()
                    out = datapath.ofproto_parser.OFPPacketOut(datapath=datapath,
                                                               buffer_id=datapath.ofproto.OFP_NO_BUFFER,
                                                               in_port=datapath.ofproto.OFPP_CONTROLLER,
                                                               actions=actions, data=ARP_Reply.data)
                    datapath.send_msg(out)
                    print("ARP Reply")
                    return True
        return False
