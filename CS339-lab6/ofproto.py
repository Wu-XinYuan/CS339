from ryu.lib.packet import ether_types
from ryu.lib.packet import  in_proto as inet

kwargs = dict(in_port=1, eth_type=ether_types.ETH_TYPE_IP,
              ipv4_src='10.0.0.1', ipv4_dst='10.0.0.2',
              ip_proto=inet.IPPROTO_UDP, udp_dst=5555)
match = parser.OFPMatch(**kwargs)
actions = [parser.OFPActionOutput(out_port)]
inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS,
                                     actions)]
mod = parser.OFPFlowMod(datapath=datapath, priority=priority,
                        match=match, instructions=inst)
datapath.send_msg(mod)