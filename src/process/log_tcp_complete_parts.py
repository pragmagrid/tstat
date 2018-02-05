conn_types = ['UNK', 'HTTP', 'RSTP', 'RTP', 'ICY', 'RTCP', 'MSN', 'YMSG', 'XMPP', 'P2P', 'SKYPE', 'SMTP', 'POP3', 'IMAP4', 'SSL', 'ED2K', 'SSH', 'RTMP', 'MSE/PE']

class tstatrecord:

    def __init__(self, line):
        t = line.split(' ')

        #Flag to detect error
        self.err = False

        if len(t) < 130:
            self.err = True
            return

        #port numbers
        self.cport          = int(t[1])      #  Client/Server TCP port  -   TCP port addresses for the client/server
        if self.cport == 22:
            self.err = True
            return

        # self.sport          = t[15]        # Client/Server TCP port  -   TCP port addresses for the client/server
        # if self.sport == 22:
        #     return ''

        #total bytes transmitted
        self.ctxdata        = int(t[8])      #  data bytes  bytes   number of bytes transmitted in the payload, including retransmissions
        self.stxdata        = int(t[22])     #  data bytes  bytes   number of bytes transmitted in the payload, including retransmissions

        #time
        self.CompleteT      = float(t[30])   # Completion time     ms  Flow duration since first packet to last packet

        #RTT time
        self.c2sAvgRTT      = float(t[44])   #  Average rtt     ms  Average RTT computed measuring the time elapsed between the data segment and the corresponding ACK

        #Retransmitted segments
        self.c2sRTO         = int(t[78])     #  rtx RTO     -   Number of retransmitted segments due to timeout expiration
        self.s2cRTO         = int(t[101])    #  rtx RTO     -   Number of retransmitted segments due to timeout expiration

        #timestamp
        self.stss           = float(t[88])   # RFC1323 ts  0/1     Timestamp option sent