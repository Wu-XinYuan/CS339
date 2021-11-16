# CS339 Lab6

邬心远

519021910604

## Q2: switch path

### solve arp storm

To make the network work, we need firstly solve the ARP-storm, or the arp package will use up all the bandwidth.

The method I used to solve this contains two step. First, assure that only the ARP package from one specific port of a switch will broadcast, thus to avoid loop. A dictionary is used to realize this:

```python
if (datapath.id, arp_src_ip, arp_dst_ip) in self.arp_in:
    # packet come back at different port.
    if self.arp_in[(datapath.id, arp_src_ip, arp_dst_ip)] != in_port:
        datapath.send_packet_out(in_port=in_port, actions=[])
        return True
    else:
        self.arp_in[(datapath.id, arp_src_ip, arp_dst_ip)] = in_port
```

Also, we need to answer to the ARP package:

```python
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
```

### Find topology and switch path:

We can use `networkx` and `topology_api` in ryu to build up the topology of the network. Then `nx.all_simple_path()`  can be used to find all the path between h1 and h2. Then to tell the switch its next switch on path to find the outport. Part of the code to build up topology and fing outport is like following:

```python
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

def get_out_port(self, datapath, src, dst, in_port):
    dpid = datapath.id
    if src not in self.G:
        self.G.add_node(src)
        self.G.add_edge(dpid, src, attr_dict={'port': in_port})
        self.G.add_edge(src, dpid)

    if dst in self.G:
        current_time = time.time()
        paths = list(nx.all_simple_paths(self.G, src, dst))
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
            next_hop = path[path.index(dpid) + 1]
            out_port = self.G[dpid][next_hop]['attr_dict']['port']
    else:
        out_port = datapath.ofproto.OFPP_FLOOD
        return out_port

```

Also, when adding flow to switches, I set hard_timeout to 5s, using 

```python
mod = parser.OFPFlowMod(datapath=datapath, priority=priority,
                        match=match, instructions=inst, hard_timeout=timeout)
```

so that after 5 seconds, the flow rule will expire and a PacketIn will happen and `get_out_port()` will give another path.

Here's the result of h1 ping h2, there is a obvious increasement of transimission time when path change:

![pic6-1](./pic/pic6-1.png)

Also, we can see how controller dispatch the path to switchers in controller's end:

![pic6-2](./pic/pic6-2.png)

## Q3: Using both paths

To using both paths, we can first change the `get_out_port()` function to return both ports if one more path is avaliable.

Then we can add group to flow table:

```python
elif len(out_ports) == 2:
    actions1 = [ofp_parser.OFPActionOutput(out_ports[0])]
    actions2 = [ofp_parser.OFPActionOutput(out_ports[1])]
    weight1 = 50
    weight2 = 50
    watch_port = ofp.OFPP_ANY
    watch_group = ofp.OFPQ_ALL
    buckets = [ofp_parser.OFPBucket(weight1, watch_port, watch_group, actions1),
               ofp_parser.OFPBucket(weight2, watch_port, watch_group, actions2)]
    group_id = 50
    req = ofp_parser.OFPGroupMod(datapath, ofp.OFPGC_ADD, ofp.OFPGT_SELECT, group_id, buckets)
    datapath.send_msg(req)
    actions = [ofp_parser.OFPActionGroup(group_id=group_id)]
```

After this, the flow table is like:

![6-3](./pic/6-3.png)

and we can see how controller add flow rule from the output information from controller:

![6-4](/home/wxy/Documents/CS339-master/CS339-lab6/pic/6-4.png)

## Q4: fast failover

To send package from h1 to h2 in one path and return from another, just small modification on `get_out_port()` function is needed, it returns two ports in the order related to src and dst:

```python
if dst in self.G:
    paths = list(nx.all_simple_paths(self.G, src, dst))
    if len(self.switch) == 0:
    	for p in paths:
    		self.switch.append(p[2])  # store s3 and s4
    for p in paths:
    	if p[2] == self.switch[self.hosts.index(src)]:
    		path = p
    next_hop = path[path.index(dpid) + 1]
    out_ports = [self.G[dpid][next_hop]['attr_dict']['port']]
    if next_hop in self.switch:
    	next_hop_sub = self.switch[1-self.switch.index(next_hop)]
    	out_ports.append(self.G[dpid][next_hop_sub]['attr_dict']['port'])
```

Then, we can use `OFPGT_FF` rule for group so package will change path when ine path is invalid:

```python
elif len(out_ports) == 2:
    action1 = [ofp_parser.OFPActionOutput(out_ports[0])]
    action2 = [ofp_parser.OFPActionOutput(out_ports[1])]
    buckets = [ofp_parser.OFPBucket(watch_port=out_ports[0], actions=action1),
               ofp_parser.OFPBucket(watch_port=out_ports[1], actions=action2)]
    group_id = int(dpid)
    req = ofp_parser.OFPGroupMod(datapath, ofp.OFPGC_ADD, ofp.OFPGT_FF, group_id, buckets)
    datapath.send_msg(req)
    actions = [ofp_parser.OFPActionGroup(group_id=group_id)]
```

The final flow table is:

![6-5](/home/wxy/Documents/CS339-master/CS339-lab6/pic/6-5.png)

We can see that s3 and s4 only has flow rules in one direction.

We can do a simple test in mininet:

![6-7](./pic/6-7.png)

when the network work properly, packets from h1 to h2 go through s3, and after we shut down a port, it will ago through s4. 
