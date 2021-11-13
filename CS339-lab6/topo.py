#!/usr/bin/env python

from mininet.net import Mininet
from mininet.node import Controller, RemoteController, OVSController
from mininet.node import CPULimitedHost, Host, Node
from mininet.node import OVSSwitch, OVSKernelSwitch, UserSwitch
from mininet.node import IVSSwitch
from mininet.cli import CLI
from mininet.log import setLogLevel, info
from mininet.link import TCLink, Intf
from subprocess import call


def myNetwork():
    net = Mininet(
        switch=OVSSwitch,
        host=CPULimitedHost, link=TCLink,
        autoStaticArp=False, controller=RemoteController)

    info('*** Adding controller\n')
    info('*** Add switches\n')
    s1 = net.addSwitch('s1')
    s2 = net.addSwitch('s2')
    s3 = net.addSwitch('s3')
    s4 = net.addSwitch('s4')

    info('*** Add hosts\n')
    h1 = net.addHost('h1', cpu=.25, cls=Host, ip='10.0.0.1', defaultRoute=None)
    h2 = net.addHost('h2', cpu=.25, cls=Host, ip='10.0.0.2', defaultRoute=None)

    info('*** Add links\n')
    net.addLink(h1, s1)
    net.addLink(s1, s3)
    net.addLink(s3, s2)
    net.addLink(s2, s4)
    net.addLink(s1, s4)
    net.addLink(s2, h2)

    info('*** Starting network\n')
    net.build()
    info('*** Starting controllers\n')
    c1 = net.addController('c1', controller=RemoteController, ip="127.0.0.1", port=6653)
    c1.start()

    info('*** Starting switches\n')
    s1.start([])
    s2.start([])
    s3.start([])
    s4.start([])

    info('*** Post configure switches and hosts\n')

    CLI(net)
    net.stop()


if __name__ == '__main__':
    setLogLevel('info')
    myNetwork()
