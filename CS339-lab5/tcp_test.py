#!/usr/bin/python

"""
Simple example of setting network and CPU parameters
"""

from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import OVSBridge
from mininet.node import CPULimitedHost
from mininet.link import TCLink
from mininet.util import quietRun, dumpNodeConnections
from mininet.log import setLogLevel, info
from mininet.cli import CLI

from sys import argv
import time


# It would be nice if we didn't have to do this:
# pylint: disable=arguments-differ


class SingleSwitchTopo(Topo):
    def build(self):
        switch1 = self.addSwitch('s1')
        switch2 = self.addSwitch('s2')
        host1 = self.addHost('h1', cpu=.1)
        host2 = self.addHost('h2', cpu=.1)
        host3 = self.addHost('h3', cpu=.1)
        host4 = self.addHost('h4', cpu=.1)
        host5 = self.addHost('h5', cpu=.1)
        host6 = self.addHost('h6', cpu=.1)
        self.addLink(host1, switch1, bw=10, delay='5ms', loss=0.05, use_htb=True)
        self.addLink(host3, switch1, bw=10, delay='5ms', loss=0.05, use_htb=True)
        self.addLink(host5, switch1, bw=10, delay='5ms', loss=0.05, use_htb=True)
        self.addLink(host2, switch2, bw=10, delay='5ms', loss=0.05, use_htb=True)
        self.addLink(host4, switch2, bw=10, delay='5ms', loss=0.05, use_htb=True)
        self.addLink(host6, switch2, bw=10, delay='5ms', loss=0.05, use_htb=True)
        self.addLink(switch1, switch2, bw=10, delay='5ms', loss=0.05, use_htb=True)


def Test(tcp):
    "Create network and run simple performance test"
    topo = SingleSwitchTopo()
    net = Mininet(topo=topo,
                  host=CPULimitedHost, link=TCLink,
                  autoStaticArp=False)
    net.start()
    info("Dumping host connections\n")
    dumpNodeConnections(net.hosts)
    # set up tcp congestion control algorithm
    output = quietRun('sysctl -w net.ipv4.tcp_congestion_control=' + tcp)
    assert tcp in output
    info("Testing bandwidth between h1 and h2 under TCP " + tcp + "\n")
    h1, h2, h3, h4, h5, h6 = net.getNodeByName('h1', 'h2', 'h3', 'h4', 'h5', 'h6')
    h1.cmd('iperf -s &')
    h2.cmd('iperf -s &')
    h3.cmd('iperf -s &')
    # h4.cmd('iperf -c 10.0.0.1 > h4.log -t 50 &')
    # h5.cmd('iperf -c 10.0.0.2 > h5.log -t 50 &')
    # h6.cmdPrint('iperf -c 10.0.0.3 > h6.log -t 50')
    h6.cmdPrint('iperf -c 10.0.0.3 -t 50')

    CLI(net)
    net.stop()


if __name__ == '__main__':
    setLogLevel('info')
    # pick a congestion control algorithm, for example, 'reno', 'cubic', 'bbr', 'vegas', 'hybla', etc.
    tcp = 'reno'
    Test(tcp)
