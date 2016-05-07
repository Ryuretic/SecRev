#####################################################################
# Ryuretic: A Modular Framework for RYU                             #
# !/mininet/examples/SecFrameTest/ICMP_Listener.py                  #
# Author:                                                           #
#   Jacob Cox (jcox70@gatech.edu)                                   #
# ICMP_Listener.py                                                #
# date 28 April 2016                                                #
#####################################################################
# Copyright (C) 1883 Thomas Edison - All Rights Reserved            #
# You may use, distribute and modify this code under the            #
# terms of the Ryuretic license, provided this work is cited        #
# in the work for which it is used.                                 #
# For latest updates, please visit:                                 #
#                   https://github.gatech.edu/jcox70/SecRevFrame    #
#####################################################################
#ref: http://stackoverflow.com/questions/8245344/python-icmp-socket-server-not-tcp-udp
#ref: http://code.activestate.com/recipes/439224-data-over-icmp/


import socket
import struct
import binascii
import sys, os
##from struct import *


def listen():
    s = socket.socket(socket.AF_INET,socket.SOCK_RAW,socket.IPPROTO_ICMP)
    s.setsockopt(socket.SOL_IP, socket.IP_HDRINCL, 1)
    ClientTable = 'mininet/examples/SecFrameTest/ClientTable.txt'
    while 1:
        data, addr = s.recvfrom(1508)
        #print s.recvfrom(1508)
        if addr == ('10.0.0.40',0):
            rcvData = data[28:]
            rcvData = rcvData.rstrip(' \t\r\n\0')
            data = rcvData.split(',')
            #print "Lenth of Received Data: ", len(data)
            if len(data) > 4:
                print "Updating Table"
                client_tbl = open(ClientTable,'a')
                client_tbl.write(rcvData+'\n')
                print data
                mac, port, passKey, violation, keyID = data
                client_tbl.close()
            else:
                print "\nValues: ", data
                if data[1] == 'd':
                    print "removing data from table"
                    lines = open(ClientTable).readlines()
                    print lines
                else:
                    print rcvData

        else: print addr

listen()
