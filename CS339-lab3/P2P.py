#!/usr/bin/env python
import time

from mininet.net import Mininet
from mininet.node import Controller, RemoteController, OVSController
from mininet.node import CPULimitedHost, Host, Node
from mininet.node import OVSKernelSwitch, UserSwitch
from mininet.node import IVSSwitch
from mininet.cli import CLI
from mininet.log import setLogLevel, info
from mininet.link import TCLink, Intf
from subprocess import call


def myNetwork():
    net = Mininet(topo=None,
                  build=False,
                  ipBase='10.0.0.0/8')

    info('*** Adding controller\n')
    info('*** Add switches\n')
    r1 = net.addHost('r1', cls=Node, ip='0.0.0.0')
    r1.cmd('sysctl -w net.ipv4.ip_forward=1')

    info('*** Add hosts\n')
    h2 = net.addHost('h2', cls=Host, ip='10.0.0.2', defaultRoute=None)
    h4 = net.addHost('h4', cls=Host, ip='10.0.0.4', defaultRoute=None)
    h1 = net.addHost('h1', cls=Host, ip='10.0.0.1', defaultRoute=None)
    h3 = net.addHost('h3', cls=Host, ip='10.0.0.3', defaultRoute=None)
    h5 = net.addHost('h5', cls=Host, ip='10.0.0.6', defaultRoute=None)
    h6 = net.addHost('h6', cls=Host, ip='10.0.0.3', defaultRoute=None)

    info('*** Add links\n')

    net.addLink(r1, h1, bw=0.000001)
    net.addLink(r1, h2, bw=0.000001)
    net.addLink(r1, h3, bw=0.000001)
    net.addLink(r1, h4, bw=0.000001)
    net.addLink(r1, h5, bw=0.000001)
    net.addLink(r1, h6, bw=0.000001)

    info('*** Starting network\n')
    net.build()
    info('*** Starting controllers\n')
    for controller in net.controllers:
        controller.start()

    info('*** Starting switches\n')

    info('*** Post configure switches and hosts\n')
    h1.cmd('ifconfig h1-eth0 192.168.10.1/24')
    h2.cmd('ifconfig h2-eth0 192.168.20.1/24')
    h3.cmd('ifconfig h3-eth0 192.168.30.1/24')
    h4.cmd('ifconfig h4-eth0 192.168.40.1/24')
    h5.cmd('ifconfig h5-eth0 192.168.50.1/24')
    h6.cmd('ifconfig h6-eth0 192.168.60.1/24')

    r1.cmd('ifconfig r1-eth0 192.168.10.2/24')
    r1.cmd('ifconfig r1-eth1 192.168.20.2/24')
    r1.cmd('ifconfig r1-eth2 192.168.30.2/24')
    r1.cmd('ifconfig r1-eth3 192.168.40.2/24')
    r1.cmd('ifconfig r1-eth4 192.168.50.2/24')
    r1.cmd('ifconfig r1-eth5 192.168.60.2/24')

    h1.cmd('route add default gw 192.168.10.2')
    h2.cmd('route add default gw 192.168.20.2')
    h3.cmd('route add default gw 192.168.30.2')
    h4.cmd('route add default gw 192.168.40.2')
    h5.cmd('route add default gw 192.168.50.2')
    h6.cmd('route add default gw 192.168.60.2')

    r1.cmd('python3 -u server.py > server.log &')
    time.sleep(1)
    h1.cmdPrint('python3 client.py -n h1 -i 192.168.10.2')
    h2.cmd('python3 client.py -n h2 -i 192.168.20.2')
    h3.cmd('python3 client.py -n h3 -i 192.168.30.2')
    h4.cmd('python3 client.py -n h4 -i 192.168.40.2')
    h5.cmd('python3 client.py -n h5 -i 192.168.50.2')
    h6.cmd('python3 client.py -n h6 -i 192.168.60.2')

    CLI(net)
    net.stop()


if __name__ == '__main__':
    setLogLevel( 'info' )
    myNetwork()

