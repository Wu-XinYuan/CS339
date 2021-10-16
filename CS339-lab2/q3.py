#!/usr/bin/env python

from sys import argv

from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import CPULimitedHost
from mininet.link import TCLink
from mininet.util import dumpNodeConnections
from mininet.log import setLogLevel, info
from mininet.cli import CLI

"""
network structure:
h1 -- s1 -- s2 -- h2
       |  /
      s3
       |
      h3
"""


class Topo1(Topo):
    def build(self):
        for h in range(3):
            # Each host gets 50%/n of system CPU
            host = self.addHost('h%s' % (h + 1))
            switch = self.addSwitch('s%s' % (h + 1))
            self.addLink(host, switch)
        # bandwidth = 10 Mbps , 5% packet loss
        self.addLink('s1', 's2', bw=10, loss=5)
        self.addLink('s1', 's3', bw=10, loss=5)
        self.addLink('s2', 's3', bw=10, loss=5)


def perfTest():
    """Create network and run simple performance test"""
    topo = Topo1()
    net = Mininet(topo=topo,
                  host=CPULimitedHost, link=TCLink,
                  autoStaticArp=True)
    net.start()
    # info("Dumping host connections\n")
    # dumpNodeConnections(net.hosts)
    h1, h2, h3 = net.getNodeByName('h1', 'h2', 'h3')
    # h1.cmdPrint('ping ' + h2.IP())
    CLI(net)
    net.stop()


if __name__ == '__main__':
    setLogLevel('info')
    # Prevent test_simpleperf from failing due to packet loss
    perfTest()
