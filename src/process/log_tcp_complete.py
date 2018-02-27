#!/opt/python/bin/python2.7

import decimal

conn_type = ['UNK', 'HTTP', 'RSTP', 'RTP', 'ICY', 'RTCP', 'MSN', 'YMSG', 'XMPP', 'P2P', 'SKYPE', 'SMTP', 'POP3', 'IMAP4', 'SSL', 'ED2K', 'SSH', 'RTMP', 'MSE/PE']

class tstatrecord:

    def __init__(self, line):
        t = line.split(' ')

        #Flag to detect error
        self.err = False
	self.err_code = 0

        if len(t) < 130:
            self.err = True
            return

        #port numbers
        self.client_port          = int(t[1])       # Client/Server TCP port - TCP port addresses for the client/server
        if self.client_port == 22:
            self.err = True
	    self.err_code = 1
            return

        self.server_port          = int(t[15])           # Client/Server TCP port - TCP port addresses for the client/server
        if self.server_port == 22:
            self.err = True
	    self.err_code = 2
            return

        self.timestamp = float(t[28]) / 1000        # First time (ms) Flow first packet since first segment ever

        #window scale
        self.client_window_scale         = int(t[66])     # window scale - Scaling values negotiated [scale factor]
        self.server_window_scale         = int(t[89])     # window scale - Scaling values negotiated [scale factor]


        #total bytes transmitted
        self.c2s_payload        = int(t[8])         # data bytes bytes number of bytes transmitted in the payload, including retransmissions
        self.s2c_payload        = int(t[22])        # data bytes bytes number of bytes transmitted in the payload, including retransmissions

        #time
        self.completion_duration_time      = float(t[30])           # Completion time (ms)  Flow duration since first packet to last packet

        #RTT time
        self.c2s_average_round_trip_time      = float(t[44])        #  Average rtt (ms)  Average RTT computed measuring the time elapsed between the data segment and the corresponding ACK
        self.s2c_average_round_trip_time      = float(t[51])        # Average rtt  (ms)  Average RTT computed measuring the time elapsed between the data segment and the corresponding ACK

        #Retransmitted segments
        self.c2s_retransmission               = int(t[9])           #number of retransmitted segments
        self.s2c_retransmission               = int(t[23])          #number of retransmitted segments
