#####################################################################
# Ryuretic: A Modular Framework for RYU                             #
# !/mininet/examples/SecFrameTest/Security_Rev_TestBed.py           #
# Author:                                                           #
#   Jacob Cox (jcox70@gatech.edu)                                   #                             #
# Security_Rev_TestBed.py                                                       #
# date 25 April 2016                                                #
#####################################################################
# Copyright (C) 1883 Thomas Edison - All Rights Reserved            #
# You may use, distribute and modify this code under the            #
# terms of the Ryuretic license, provided this work is cited        #
# in the work for which it is used.                                 #
# For latest updates, please visit:                                 #
#                   https://github.gatech.edu/jcox70/SecRevFrame    #
#####################################################################

###################################################
#!/usr/bin/python
#!/mininet/examples/SecFrameTest
# author: Jacob Cox
# Security_Rev_TestBed.py
# date 30 July 2015
###################################################
"""How To Run This Program """
###################################################
"""
This program sets up a mininet architecture consisting of one NAT router,
one switch, one dhcp server, and 6 hosts. IPs are only assigned to the
NAT router and the DHCP server. Hosts are not assigned IPs until a dhclient
request is made to obtain IPS from the DHCP server.
"""
#Program requirements
"""

"""
#Instructions:
"""
1)  a) sudo mn -c
    b) sudo python Security_Rev_TestBed.py


2) To shutdown:
    a) In terminal 2, hit cntl+c (exit pyretic controller)
    b) In terminal 1, type exit
    c) In terminal 1, type sudo mn -c
"""

from mininet.topo import Topo
from mininet.net import Mininet
from mininet.link import TCLink
from mininet.util import custom
from mininet.node import RemoteController,OVSSwitch
from mininet.log import setLogLevel, info
from mininet.nodelib import NAT
from mininet.cli import CLI
from mininet.util import run


#Topology to be instantiated in Mininet
class RevocationTopo(Topo):
    "Mininet Security Rev Test topology"
    
    def __init__(self, cpu=.1, max_queue_size=None, **params):
        '''
        nat+--+              +-----------+h1
              |              +-----------+h2
              +-------+s1+---+-----------+h3
                DHC+---+     +-----------+h4
                             +-----------+h5
                             +-----------+h6
        '''
        # Initialize topo
        Topo.__init__(self, **params)
        ###Thanks to Sean Donivan for the NAT code####
        natIP= '10.0.1.222'
        # Host and link configuration
        hostConfig = {'cpu': cpu, 'defaultRoute': 'via ' + natIP }
        LinkConfig = {'bw': 10, 'delay': '1ms', 'loss': 0,
                   'max_queue_size': max_queue_size }
        #################################################

        #add Single Switch
        s1  = self.addSwitch('s1', protocols='OpenFlow13')

        # add DHCP server
##        dhcp1 = self.addHost('dhcp1', ip='10.0.1.200/24')
##        self.addLink(s1, dhcp1, 1, 1)
        
        #add six hosts with IP assigned 
        h1 = self.addHost('h1', mac='00:00:00:00:00:01', ip="10.0.0.1", **hostConfig)
        self.addLink(s1, h1, 1, 1, **LinkConfig)
        
        h2 = self.addHost('h2', mac='00:00:00:00:00:02', ip="10.0.0.2", **hostConfig)
        self.addLink(s1, h2, 2, 1, **LinkConfig)
        
        h3 = self.addHost('h3', mac='00:00:00:00:00:03', ip="10.0.0.3", **hostConfig)
        self.addLink(s1, h3, 3, 1, **LinkConfig)
        
        h4 = self.addHost('h4', mac='00:00:00:00:00:04', ip="10.0.0.4", **hostConfig)
        self.addLink(s1, h4, 4, 1, **LinkConfig)
        
        h5 = self.addHost('h5', mac='00:00:00:00:00:05', ip="10.0.0.5", **hostConfig)
        self.addLink(s1, h5, 5, 1, **LinkConfig)
        
        h6 = self.addHost('h6', mac='00:00:00:00:00:06', ip="10.0.0.6", **hostConfig)
        self.addLink(s1, h6, 6, 1, **LinkConfig)

        # Create and add NAT
        self.nat = self.addNode( 'nat', cls=NAT, ip=natIP,
                            inNamespace=False)	
        self.addLink(s1, self.nat, port1=8 )	


if __name__ == '__main__':
    info('*** Starting Mininet *** \n')
    print '*** Starting Mininet *** \n'
    topo = RevocationTopo()
    net = Mininet(topo=topo, link=TCLink, controller=RemoteController)
    info('*** Topology Created *** \n')
    print "***Toplology Created***"
    
    net.start()
    run("ovs-vsctl set bridge s1 protocols=OpenFlow13")
    

    info('***attempting to start dhcp server***')
    #net.get('dhcp1').cmd('sudo /etc/init.d/isc-dhcp-server start')
    #net.get('dhcp1').cmd('sudo wireshark &')
    #info('***Starting Wireshark...*** \n')
    #raw_input("\nPress Enter once Wireshark is capturing trafic \n")
    #info('*** Assigning IP to h1 and h2 (See Wireshark) *** \n')
    #net.get('h1').cmd('dhclient')
    #net.get('h2').cmd('dhclient')
    info('*** Running CLI *** \n')
    CLI( net )

    info ('*** Stopping Network ***')
    #net.get('dhcp1').cmd('sudo /etc/init.d/isc-dhcp-server stop')
    net.stop()

# ps -A | grep controller
# sudo fuser -k 6633/tcp
# pyretic.py -v high pyretic.modules.arp
# sudo fuser -k 6633/tcp

"""
Install DHCP Server:
    a) Open terminal, type ifconfig, record eth0 address
    b) enter: sudo apt-get update
    c) enter: sudo apt-get install isc-dhcp-server
    d) accept defaults
2) Modify dhcp.conf file:
    a) enter nano -w /etc/dhcp/dhcpd.conf
    b) Place the below lines of code into the file
    --------------------------------------------------------
    # A slightly different configuration for an internal subnet.
    subnet 10.0.1.0 netmask 255.255.255.0 {
      range 10.0.0.10 10.0.0.30;
      option domain-name-servers 10.0.1.223, 8.8.4.4;
    #  option domain-name "internal.example.org";
      option routers 10.0.1.222;
      option broadcast-address 10.0.1.255;
      default-lease-time 600;
      max-lease-time 7200;
    }
    --------------------------------------------------------  
3) Open second terminal:
    a) type: cd pyretic/pyretic/modules
    b) type: sudo fuser -k 6633/tcp
    c) type: pyretic.py -v high pyretic.modules.arp
    d) pyretic controller is now running
4) In the first terminal:
    a) type: cd ~
    b) type: sudo mn -c
    c) type: sudo python DHCP_Min.py
    d) This will build your topology, activate your dhcp server,
       initializes wireshark, and waits for user to configure
       wireshark (select ok, ok, dhcp1-eth0, start)
    e) hit enter.
    f) Program runs dhclient on h1 and h2. Wireshark and Terminal
       2 will display dhcp client requests, arps, etc.
    g) test network with commands and observe terminal 2 & wireshark
        1] h1 ping -c2 h2
        2] h3 ifconfig
        3] h3 dhclient ifconfig h3
        4] h3 ifconfig
        5] h2 wget themilpost.com
    h) Check dhcp server leases
        1] type xterm dhcp1
        2} in xterm type: sudo tail /var/lib/dhcp/dhcpd.leases
"""
