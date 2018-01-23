#!/usr/bin/python

import decimal

conn_types = ['UNK', 'HTTP', 'RSTP', 'RTP', 'ICY', 'RTCP', 'MSN', 'YMSG', 'XMPP', 'P2P', 'SKYPE', 'SMTP', 'POP3', 'IMAP4', 'SSL', 'ED2K', 'SSH', 'RTMP', 'MSE/PE']

class tstatrecord:
    def __init__(self, line):
        t = line.split(' ')
        # C2S                           Short description
        self.cip            = t[0]      #   Client/Server IP addr   -   IP addresses of the client/server
        self.cport          = t[1]      #   Client/Server TCP port  -   TCP port addresses for the client/server
        self.c2spckt        = t[2]      #   packets     -   total number of packets observed form the client/server
        self.cressent       = t[3]      #   RST sent    0/1     0 = no RST segment has been sent by the client/server
        self.cackssent      = t[4]      #   ACK sent    -   number of segments with the ACK field set to 1
        self.cpureackssent  = t[5]      #   PURE ACK sent   -   number of segments with ACK field set to 1 and no data
        self.csentbytes     = t[6]      #   unique bytes    bytes   number of bytes sent in the payload
        self.cdatapckt      = t[7]      #   data pkts   -   number of segments with payload
        self.ctxdata        = t[8]      #   data bytes  bytes   number of bytes transmitted in the payload, including retransmissions
        self.crtxpckt       = t[9]      #   rexmit pkts     -   number of retransmitted segments
        self.crtxdata       = t[10]     #    rexmit bytes    bytes   number of retransmitted bytes
        self.coutseqpckt    = t[11]     #    out seq pkts    -   number of segments observed out of sequence
        self.csynpckt       = t[12]     #    SYN count   -   number of SYN segments observed (including rtx)
        self.cfinpckt       = t[13]     #    FIN count   -   number of FIN segments observed (including rtx)

        # S2C                           Short description   Unit    Long description
        self.sip            = t[14]     # Client/Server IP addr   -   IP addresses of the client/server
        self.sport          = t[15]     # Client/Server TCP port  -   TCP port addresses for the client/server
        self.s2cpckt        = t[16]     # packets     -   total number of packets observed form the client/server
        self.sressent       = t[17]     # RST sent    0/1     0 = no RST segment has been sent by the client/server
        self.sackssent      = t[18]     # ACK sent    -   number of segments with the ACK field set to 1
        self.spureackssent  = t[19]     # PURE ACK sent   -   number of segments with ACK field set to 1 and no data
        self.ssentbytes     = t[20]     # unique bytes    bytes   number of bytes sent in the payload
        self.sdatapckt      = t[21]     # data pkts   -   number of segments with payload
        self.stxdata        = t[22]     # data bytes  bytes   number of bytes transmitted in the payload, including retransmissions
        self.srtxpckt       = t[23]     # rexmit pkts     -   number of retransmitted segments
        self.srtxdata       = t[24]     # rexmit bytes    bytes   number of retransmitted bytes
        self.soutseqpckt    = t[25]     # out seq pkts    -   number of segments observed out of sequence
        self.ssynpckt       = t[26]     # SYN count   -   number of SYN segments observed (including rtx)
        self.sfinpckt       = t[27]     # FIN count   -   number of FIN segments observed (including rtx)

        # Further flow features
        self.fpckt          = t[28]  # First time  ms  Flow first packet since first segment ever
        self.lpckt          = t[29]  # Last time   ms  Flow last segment since first segment ever
        self.comlp          = t[30]  # Completion time     ms  Flow duration since first packet to last packet
        self.cfpckt         = t[31]  # C first payload     ms  Client first segment with payload since the first flow segment
        self.sfpckt         = t[32]  # S first payload     ms  Server first segment with payload since the first flow segment
        self.clpckt         = t[33]  # C last payload  ms  Client last segment with payload since the first flow segment
        self.slpckt         = t[34]  # S last payload  ms  Server last segment with payload since the first flow segment
        self.cfack          = t[35]  # C first ack     ms  Client first ACK segment (without SYN) since the first flow segment
        self.sfack          = t[36]  # S first ack     ms  Server first ACK segment (without SYN) since the first flow segment
        self.cipint         = t[37]  # C Internal  0/1     1 = client has internal IP, 0 = client has external IPself.                = t[
        self.sipint         = t[38]  # S Internal  0/1     1 = server has internal IP, 0 = server has external IP
        self.ciscrypto      = t[39]
        self.siscrypto      = t[40]
        self.conntype       = t[41]
        self.P2Ptype        = t[42]
        self.HTTPtype       = t[43]

        #TCP End to End Set
        self.c2savgrtt      = t[44]  # Average rtt     ms  Average RTT computed measuring the time elapsed between the data segment and the corresponding ACK
        self.c2sminrtt      = t[45]  # rtt min     ms  Minimum RTT observed during connection lifetime
        self.c2savgmaxrtt   = t[46]  # rtt max     ms  Maximum RTT observed during connection lifetime
        self.c2sstdrtt      = t[47]  # Stdev rtt   ms  Standard deviation of the RTT
        self.c2srttsamples  = t[48]  # rtt count   -   Number of valid RTT observation
        self.c2sttlmin      = t[49]  # ttl_min     -   Minimum Time To Live
        self.c2sttlmax      = t[50]  # ttl_max     -   Maximum Time To Live
        self.s2cavgrtt      = t[51]  # Average rtt     ms  Average RTT computed measuring the time elapsed between the data segment and the corresponding ACK
        self.s2cminrtt      = t[52]  # rtt min     ms  Minimum RTT observed during connection lifetime
        self.s2cavgmaxrtt   = t[53]  # rtt max     ms  Maximum RTT observed during connection lifetime
        self.s2cstdrtt      = t[54]  # Stdev rtt   ms  Standard deviation of the RTT
        self.s2crttsamples  = t[55]  # rtt count   -   Number of valid RTT observation
        self.s2cttlmin      = t[56]  # ttl_min     -   Minimum Time To Live
        self.s2cttlmax      = t[57]  # ttl_max     -   Maximum Time To Live

        #TCP P2P set
        self.P2Pst          = t[58]     #P2P protocol message type, as identified by the IPP2P engine (see ipp2p_tstat.c)
        self.ED2Kdata       = t[59]     #For P2P ED2K flows, the number of data messages
        self.ED2Ksig        = t[60]     #For P2P ED2K flows, the number of signaling (not data) messages
        self.ED2Kc2s        = t[61]     #For P2P ED2K flows, the number of client<->server messages
        self.ED2kc2c        = t[62]     #For P2P ED2K flows, the number of client<->client messages
        self.ED2Kchat       = t[63]     #For P2P ED2K flows, the number of chat messages

        #TCP Option set
        self.cws            = t[64]     #    RFC1323 ws  0/1     Window scale option sent
        self.ctss           = t[65]     #    RFC1323 ts  0/1     Timestamp option sent
        self.cwsneg         = t[66]     #    window scale    -   Scaling values negotiated [scale factor]
        self.csackr         = t[67]     #    SACK req    0/1     SACK option set
        self.csacks         = t[68]     #    SACK sent   -   number of SACK messages sent
        self.cMssdec        = t[69]     #    MSS     bytes   MSS declared
        self.cMssmeas       = t[70]     #    max seg size    bytes   Maximum segment size observed
        self.cmssmeas       = t[71]     #    min seg size    bytes   Minimum segment size observed
        self.cMrw           = t[72]     #    win max     bytes   Maximum receiver window announced (already scale by the window scale factor)
        self.cmrw           = t[73]     #    win min     bytes   Maximum receiver windows announced (already scale by the window scale factor)
        self.cwz            = t[74]     #    win zero    -   Total number of segments declaring zero as receiver window
        self.cMwin          = t[75]     #    cwin max    bytes   Maximum in-flight-size computed as the difference between the largest sequence number so far, and the corresponding last ACK message on the reverse path. It is an estimate of the congestion window
        self.cmwin          = t[76]     #    cwin min    bytes   Minimum in-flight-size
        self.ciwin          = t[77]     #    initial cwin    bytes   First in-flight size, or total number of unack-ed bytes sent before receiving the first ACK segment

        self.c2srto         = t[78]     #    rtx RTO     -   Number of retransmitted segments due to timeout expiration
        self.c2srfr         = t[79]     #    rtx FR  -   Number of retransmitted segments due to Fast Retransmit (three dup-ack)
        self.c2sreord       = t[80]     #    reordering  -   Number of packet reordering observed
        self.c2sdup         = t[81]     #    net dup     -   Number of network duplicates observed
        self.c2sunk         = t[82]     #    unknown     -   Number of segments not in sequence or duplicate which are not classified as specific events
        self.c2cflcntl      = t[83]     #    flow control    -   Number of retransmitted segments to probe the receiver window
        self.c2sunnecrto    = t[84]     #    unnece rtx RTO  -   Number of unnecessary transmissions following a timeout expiration
        self.c2sunnecfr     = t[85]     #    unnece rtx FR   -   Number of unnecessary transmissions following a fast retransmit
        self.c2srsyn        = t[86]     #    != SYN seqno    0/1     1 = retransmitted SYN segments have different initial seqno

        self.sws            = t[87]     # RFC1323 ws  0/1     Window scale option sent
        self.stss           = t[88]     # RFC1323 ts  0/1     Timestamp option sent
        self.swsneg         = t[89]     # window scale    -   Scaling values negotiated [scale factor]
        self.ssackr         = t[90]     # SACK req    0/1     SACK option set
        self.ssacks         = t[91]     # SACK sent   -   number of SACK messages sent
        self.sMssdec        = t[92]     # MSS     bytes   MSS declared
        self.sMssmeas       = t[93]     # max seg size    bytes   Maximum segment size observed
        self.smssmeas       = t[94]     # min seg size    bytes   Minimum segment size observed
        self.sMrw           = t[95]     # win max     bytes   Maximum receiver window announced (already scale by the window scale factor)
        self.smrw           = t[96]     # win min     bytes   Maximum receiver windows announced (already scale by the window scale factor)
        self.swz            = t[97]     # win zero    -   Total number of segments declaring zero as receiver window
        self.sMwin          = t[98]     # cwin max    bytes   Maximum in-flight-size computed as the difference between the largest sequence number so far, and the corresponding last ACK message on the reverse path. It is an estimate of the congestion window
        self.smwin          = t[99]     # cwin min    bytes   Minimum in-flight-size
        self.siwin          = t[100]     # initial cwin    bytes   First in-flight size, or total number of unack-ed bytes sent before receiving the first ACK segment
        self.s2crto         = t[101]     # rtx RTO     -   Number of retransmitted segments due to timeout expiration
        self.s2crfr         = t[102]     # rtx FR  -   Number of retransmitted segments due to Fast Retransmit (three dup-ack)
        self.s2creord       = t[103]     # reordering  -   Number of packet reordering observed
        self.s2cdup         = t[104]     # net dup     -   Number of network duplicates observed
        self.s2cunk         = t[105]     # unknown     -   Number of segments not in sequence or duplicate which are not classified as specific events
        self.s2cflcntl      = t[106]     # flow control    -   Number of retransmitted segments to probe the receiver window
        self.s2cunnecrto    = t[107]     # unnece rtx RTO  -   Number of unnecessary transmissions following a timeout expiration
        self.s2cunnecfr     = t[108]     # unnece rtx FR   -   Number of unnecessary transmissions following a fast retransmit
        self.s2crsyn        = t[109]     # != SYN seqno    0/1     1 = retransmitted SYN segments have different initial seqno

        #TCP Layer 7 Set
        self.HTTPreq            = t[110]    #Number of HTTP Requests (GET/POST/HEAD) seen in the C2S direction (for HTTP connections)
        self.HTTPres            = t[111]    #Number of HTTP Responses (HTTP) seen in the S2C direction (for HTTP connections)
        self.fHTTPres           = t[112]    #First HTTP Response code seen in the server->client communication (for HTTP connections)
        self.cpktspush          = t[113]    #number of push separated messages C2S
        self.spktspush          = t[114]    #number of push separated messages S2C
        self.ctlsSNI            = t[115]    #For TLS flows, the server name indicated by the client in the Hello message extensions
        self.stlsSCN            = t[116]    #For TLS flows, the subject CN name indicated by the server in its certificate
        self.cnpnalpn           = t[117]    #For TLS flows, a bitmap representing the usage of NPN/ALPN for HTTP2/SPDY negotiation
        self.snpnalpn           = t[118]    #For TLS flows, a bitmap representing the usage of NPN/ALPN for HTTP2/SPDY negotiation
        self.ctlssesid          = t[119]    #For TLS flows, indicates that the Client Hello carries an old Session ID
        self.clasthandshake     = t[120]    #For TLS flows, time of Client last packet seen before first Application Data (relative)
        self.slasthandshak      = t[121]    #For TLS flows, time of Server last packet seen before first Application Data (relative)
        self.cappdataT          = t[122]    #For TLS flows, time between the Client first Application Data message and the first flow segment
        self.sappdataT          = t[123]    #For TLS flows, time between the Server first Application Data message and the first flow segment
        self.cappdataB          = t[124]    #For TLS flows, relative sequence number for the Client first Application Data message
        self.sappdataB          = t[125]    #For TLS flows, relative sequence number for the Client first Application Data message
        self.fqdn               = t[126]    #Fully Qualified Domain Name recovered using DNHunter
        self.dnsrslv            = t[127]    #IP address of the contacted DNS resolver
        self.dnsreqT            = t[128]    #unixtime (in ms) of the DNS request
        self.dnsresT            = t[129]    #unixtime (in ms) of the DNS response




        # if len(t) == 119:
        #     self.fqdn           = t[-8:-5]      # Fully qualified domain name
        #     self.fqdnr          = t[-1][:-1]    # Reversed fqdn
        # else:
        #     self.fqdn       = None
        #     self.fqdnr      = ''
        # self.conntype       = t[100]        # Bitmask stating the connection type as identified by TCPL7 inspection engine (see protocol.h)