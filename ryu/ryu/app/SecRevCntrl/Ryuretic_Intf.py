#####################################################################
# Ryuretic: A Modular Framework for RYU                             #
# !/ryu/ryu/app/SecRevCntrl/Ryuretic_Intf.py                        #
# Authors:                                                          #
#   Jacob Cox (jcox70@gatech.edu)                                   #
#   Sean Donovan (sdonovan@gatech.edu)                              #
# Ryuretic_Intf.py                                                  #
# date 28 April 2016                                                #
#####################################################################
# Copyright (C) 1883 Thomas Edison - All Rights Reserved            #
# You may use, distribute and modify this code under the            #
# terms of the Ryuretic license, provided this work is cited        #
# in the work for which it is used.                                 #
# For latest updates, please visit:                                 #
#                   https://github.gatech.edu/jcox70/SecRevFrame    #
#####################################################################
"""How To Run This Program
1) Ensure you have Ryu installed.
2) Save the following files to /home/ubuntu/ryu/ryu/app/
    a) Ryuretic_Intf.py
    b) Ryuretic.py
    c) Pkt_Parse.py
    d) switch_mod.py
2) In your controller terminal type: cd ryu
3) Enter PYTHONPATH=. ./bin/ryu-manager ryu/app/Ryuretic_Intf.py
"""
#####################################################################
from Ryuretic import coupler
#[1] Import needed libraries here
import string, random

class Ryuretic_coupler(coupler):
    def __init__(self, *args, **kwargs):
        super(Ryuretic_coupler, self).__init__(*args, **kwargs)

        ##############      Add User Variables     ###############
        #[2] Add new variables here.
        self.stat_Fw_tbl = {}
        self.cntrl ={'mac': 'ca:ca:ca:ab:ab:ab','ip':'10.0.0.40',
                     'port':None}
        self.badhost = {'mac':'00:00:00:00:00:02', 'ip':'10.0.0.2'}
        self.policyTbl = {}
        self.actionTbl = {}
        self.netView = {}
        self.keyID = 101
        self.t_agent = {}
        ICMP_ECHO_REPLY = 0
        ICMP_ECHO_REQUEST = 8
    
    ##############         Proactive Rule Sets    #################
    #[3] Insert proactive rules defined below. Follow format below
    #    Options include drop or redirect, fwd is the default. 
    def get_proactive_rules(self, dp, parser, ofproto):
        # return None, None
        fields, ops = self.honeypot(dp, parser, ofproto)
        return fields, ops

    ################       Reactive Rule Sets     #################
    #[4] use below handles to direct packets to reactive user modules 
    #    defined in location #[5]. If no rule is added, then
    #    the default self.default_Fields_Ops(pkt) must be used  
    def handle_eth(self,pkt):
        print "handle eth"
        fields, ops = self.default_Field_Ops(pkt)
        self.install_field_ops(pkt,fields,ops)

    def handle_arp(self,pkt):
        print "\n******handle ARP******\n"
        #fields, ops = self.respond_to_arp(pkt)
        fields, ops = self.detectSpoof(pkt)
        #fields, ops = self.default_Field_Ops(pkt)
        print"Installing Field OPs"
        self.install_field_ops(pkt, fields, ops)
		
    def handle_ip(self,pkt):
        print "handle ip"
	#fields, ops = self.default_Field_Ops(pkt)
        fields, ops = self.Stateful_FW(pkt)
	##############################################################
        #Determine highest priority fields and ops pair, if needed
        #xfields = [fields0, fields1, fields2]
        #xops = [ops0, ops1, ops2]
        #fields,ops = self._build_FldOps(xfields,xops)
	##############################################################
        
        self.install_field_ops(pkt,fields,ops)

    def handle_icmp(self,pkt):
        print "\n**********handle icmp********\n"
        fields, ops = self.respond_to_ping(pkt)
        #fields, ops = self.default_Field_Ops(pkt)
        self.install_field_ops(pkt, fields, ops)

    def handle_tcp(self,pkt):
        print "handle tcp"
        #fields, ops = self.default_Field_Ops(pkt)
        fields,ops = self.Simple_FW(pkt)
        #fields, ops = self.TTL_Check(pkt)
        # users can also call modules with no return
        self.install_field_ops(pkt, fields, ops)

    def handle_udp(self,pkt):
        print "handle udp"
        fields, ops = self.default_Field_Ops(pkt)
        #fields, ops = self.TTL_Check(pkt)
        self.install_field_ops(pkt, fields, ops)

    def handle_unk(self,pkt):
        print "handl unk"
        fields, ops = self.default_Field_Ops(pkt)
        self.install_field_ops(pkt, fields, ops)


    # The following are from the old NFG file.
    def default_Field_Ops(self,pkt):
        def _loadFields(pkt):
            #keys specifies match fields for action. Default is
            #inport and #srcmac. ptype icmp, udp, etc.
            print "loading fields"
            fields = {'keys':['inport','srcmac'],'ptype':[], 
                      'dp':pkt['dp'], 'ofproto':pkt['ofproto'], 
                      'msg':pkt['msg'], 'inport':pkt['inport'], 
                      'srcmac':pkt['srcmac'], 'ethtype':None, 
                      'dstmac':None, 'srcip':None, 'proto':None, 
                      'dstip':None, 'srcport':None, 'dstport':None,
                      'com':None}
            return fields
    
        def _loadOps():
            print "Loading ops"
            #Specifies the timeouts, priority, operation and outport
            #options for op: 'fwd','drop', 'mir', 'redir', 'craft'
            ops = {'hard_t':None, 'idle_t':None, 'priority':0, \
                   'op':'fwd', 'newport':None}
            return ops
        
        print "default Field_Ops called"
        fields = _loadFields(pkt)
        ops = _loadOps()
        return fields, ops


    #############  Ryuretic Network Application Modules    ##########
    #[5] Add user created methods below. Examples are provided to assist
    # the user with basic python, dictionary, list, and function calls

    def respond_to_arp(self,pkt):
        #print 'Respond to Arp Called'
        fields, ops = self.default_Field_Ops(pkt)
        if pkt['dstip'] == self.cntrl['ip']:
            print "Message to Controller"
            fields['dstip'] = pkt['srcip']
            fields['srcip'] = self.cntrl['ip']
            fields['dstmac'] = pkt['srcmac']
            fields['srcmac'] = self.cntrl['mac']
            fields['ptype'] = 'arp'
            fields['ethtype'] = 0x0806
            ops['op'] = 'craft'
            ops['newport'] = pkt['inport']
            #print "INPORT: ", pkt['inport']
        return fields, ops
            

    def respond_to_ping(self,pkt):
        fields, ops = self.default_Field_Ops(pkt)
        #print "\n\nRespond to Ping"
        if pkt['dstip'] == self.cntrl['ip']:
            if pkt['srcip'] == '10.0.0.1':
                  self.t_agent = {'srcip':pkt['srcip'],'srcmac':pkt['srcmac'],
                                  'inport':pkt['inport'],'msg':pkt['msg'],
                                  'ofproto':pkt['ofproto'], 'dp':pkt['dp']}
                                  
            #print'respond to ping'
            rcvData = pkt['data'].data
            fields['dstip'] = pkt['srcip']
            fields['srcip'] = self.cntrl['ip']
            fields['dstmac'] = pkt['srcmac']
            fields['srcmac'] = self.cntrl['mac']
            
            fields['ptype'] = 'icmp'
            fields['ethtype'] = 0x0800
            fields['proto'] = 1
            fields['com'] = 'received '+rcvData
            ops['op'] = 'craft'
            ops['newport'] = pkt['inport']

        return fields, ops
        

    def sendICMP_msg(self,pkt):
        print'Sending ICMP message'
        rcvData = pkt['data'].data
        #print type(rcvData)
        fields['dstip'] = pkt['srcip']
        fields['srcip'] = self.cntrl['ip']
        fields['dstmac'] = pkt['srcmac']
        fields['srcmac'] = self.cntrl['mac']
        
        fields['ptype'] = 'icmp'
        fields['ethtype'] = 0x0800
        fields['proto'] = 1
        fields['com'] = fields['srcmac']+','+str(fields['inport'])+',passkey,violation'
        ops['op'] = 'craft'
        ops['newport'] = pkt['inport']

        return fields, ops

    def update_TA(self,pkt,passkey,violation):
        #print "Updating Trusted Agent"
        fields, ops = {},{}
        fields['keys'] = ['inport', 'srcip']
        fields['dstip'] = self.t_agent['srcip']
        fields['srcip'] = self.cntrl['ip']
        fields['dstmac'] = self.t_agent['srcmac']
        fields['srcmac'] = self.cntrl['mac']
        fields['dp'] = self.t_agent['dp']
        fields['msg'] = self.t_agent['msg']
        fields['inport'] = self.t_agent['inport']
        fields['ofproto']=self.t_agent['ofproto']
        fields['ptype'] = 'icmp'
        fields['ethtype'] = 0x0800
        fields['proto'] = 1
        fields['com'] = pkt['srcmac']+','+str(pkt['inport'])+\
                        ','+str(passkey)+','+violation+','+str(self.keyID)
        
        ops = {'hard_t':None, 'idle_t':None, 'priority':0, \
                   'op':'fwd', 'newport':None}
        ops['op'] = 'craft'
        ops['newport'] = self.t_agent['inport']
        
        self.install_field_ops(pkt, fields, ops)

        
    # trying to forward to respond_to_ARP to consolidate code
    def detectSpoof(self,pkt):
        #print "Detect Spoof calls Respond to ARP\n"
        policyFlag = False
        fields, ops = self.respond_to_arp(pkt)
        # Check network view to see if ip matches flowgraph
        if self.netView.has_key(pkt['inport']):
            if pkt['srcmac'] != self.netView[pkt['inport']]['srcmac']:
                print "Spoofed MAC Detected"
                policyFlag = True
            if pkt['srcip'] != self.netView[pkt['inport']]['srcip']:
                print "Spoofed IP detected"
                policyFlag = True
        else:
            self.netView[pkt['inport']] = {'srcmac': pkt['srcmac'],
                                           'srcip': pkt['srcip']}

        if policyFlag == True:
            keyID = self.keyID
            self.keyID += 1
            print "Adding Violation, passkey, and updating keyID"
            violation = 's'
            #create passkey
            passkey =''.join(random.choice(string.ascii_letters) for x in range(8))
            #update policy table
            self.policyTbl[keyID]={'inport':pkt['inport'],
                                        'srcmac':pkt['srcmac'],
                                        'passkey':passkey,
                                        'violation':violation}
            #Notify trusted agent of newly flagged client
            self.update_TA(pkt,passkey, violation)
            #Update action table to handle future client packets
            fields['keys'] = ['inport']
            ops['dstmac'] = self.t_agent['srcmac']
            ops['dstip'] = self.t_agent['srcip']
            ops['op'] = 'redir'
            ops['newport'] = self.t_agent['inport']
            ops['priority'] = 1000
            ops['idle_t'] = 180
            ops['hard_t'] = 180
            
            #print "Updating Action Table\n"
            self.actionTbl[pkt['srcmac']] = {'keyID':self.keyID,
                                             'fields':fields,
                                             'ops':ops}
        return fields, ops

    def Arp_Poison(self,pkt):

        fields['ptype'] = 'arp'
        fields['srcmac'] = self.t_agent['srcmac']
        fields['dstmac'] = pkt['srcmac']
        fields['srcip'] = self.t_agent['srcip']
        fields['dstip'] = pkt['srcip']

        ops = {'hard_t':None, 'idle_t':None, 'priority':0, \
                   'op':'craft', 'newport':None}

        self.install_field_ops(pkt, fields, ops)
         
            
    def Simple_FW(self,pkt):
        fields, ops = self.default_Field_Ops(pkt)
        #blocking w3cschools and facebook
        if pkt['dstip'] in ['141.8.225.80', '173.252.120.68']:
            print "W3Cschools or Facebook is not allowed"
            #tell controller to drop pkts destined for dstip
            fields['keys'],fields['dstip'] = ['dstip'],pkt['dstip']
            ops['priority'] = 100
            ops['op']= 'drop'
        return fields, ops
        
    #Block IP packets with decremented TTL
    def TTL_Check(self, pkt):
        print "TTL Check called"
        fields, ops = self.default_Field_Ops(pkt)
       # print "\n*******pkt_in_handler - TTL_Check********"
        if pkt['ttl'] == 63 or pkt['ttl'] == 127:
            print "XxXxXx  NAT Detected  xXxXxX"
            #drop all packets from port with TTL decrement
            fields['keys'] = ['inport']
            fields['inport'] = pkt['inport']
            ops['priority'] = 100
            ops['op']='drop'
        return fields, ops

    def Stateful_FW(self,pkt):
        fields, ops = self.default_Field_Ops(pkt)
        if pkt['input'] in [1,2,3,4,5,6,7,8]:
            if self.stat_Fw_tbl.has_key(pkt['srcip']):
                if len(self.stat_Fw_tbl[pkt['srcip']]['dstip']) > 4:
                    self.stat_Fw_tbl[pkt['srcip']]['dstip'].pop(3)
                self.self.stat_Fw_tbl[pkt['srcip']]['dstip'].append(pkt['dstip'])
            else:
                self.stat_Fw_tbl[pkt['srcip']]={'dstip':[pkt['dstip']]}
            return fields, ops
        else:
            if self.stat_Fw_tbl.has_key(pkt['dstip']):
                if pkt['srcip'] in stat_Fw_tbl[pkt['dstip']]['dstip']:
                    return fields, ops
                else:
                    fields['keys'] = ['srcip','dstip']
                    fields['srcip'] = pkt['srcip']
                    fields['dstip'] = pkt['dstip']
                    ops['priority'] = 100
                    ops['op']='drop'
                    ops['hard_t'] = 20
                    ops['idle_t'] = 4
                    return fields, ops

    def honeypot(self, dp, parser, ofproto):
        # This should install proactive rules that mirrors data from a 
        # honeypot system
        fields, ops = {}, {}
        fields['eth_type'] = 0x0800
        fields['keys'] = ['srcip']
        fields['srcip'] = '10.0.0.42'
        ops['priority'] = 100
        ops['op'] = 'mir'
        ops['newport'] = 2
        #could make this multicast as well [1,2,3]

        return fields, ops
