#!/opt/python/bin/python2.7

from decimal import *

conn_type = ['UNK', 'HTTP', 'RSTP', 'RTP', 'ICY', 'RTCP', 'MSN', 'YMSG', 'XMPP', 'P2P', 'SKYPE', 'SMTP', 'POP3', 'IMAP4', 'SSL', 'ED2K', 'SSH', 'RTMP', 'MSE/PE']

class tstatrecord:

    def __init__(self, line):
        t = line.split(' ')

        #Flag to detect error
        self.err = False
	self.err_code = 0

        if len(t) < 130:
            self.err = True
            self.err_code = 1
            print("Length is less than 130")
            return

        #port numbers
        self.client_port          = t[1]       # Client/Server TCP port - TCP port addresses for the client/server
        if self.client_port == "22":
            self.err = True
            return

        self.server_port          = t[15]           # Client/Server TCP port - TCP port addresses for the client/server
        if self.server_port == "22":
            self.err = True
            return

        self.timestamp = t[28]        # First time (ms) Flow first packet since first segment ever

        self.cip = t[0]
        #Server IP address
        self.sip = t[14]
        #window scale
        self.client_window_scale         = t[66]
        self.server_window_scale         = t[89]     # window scale - Scaling values negotiated [scale factor]

        #total bytes transmitted
        self.c2s_payload        = t[8]
        self.s2c_payload        = t[22]        # data bytes bytes number of bytes transmitted in the payload, including retransmissions

        #time
        self.completion_duration_time      = t[30]           # Completion time (ms)  Flow duration since first packet to last packet

        #RTT time
        self.c2s_average_round_trip_time      = t[44]
        self.s2c_average_round_trip_time      = t[51]        # Average rtt  (ms)  Average RTT computed measuring the time elapsed between the data segment and the corresponding ACK

        #Retransmitted segments
        self.c2s_retransmission               = t[9]
        self.s2c_retransmission               = t[23]          #number of retransmitted segments
