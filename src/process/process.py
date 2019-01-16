#!/opt/python/bin/python2.7

import log_tcp_complete as tstat
import time
import config

class run:

    total = 0
    total_err = 0

    def fileread(self, filename, dirname, db):

        f = open(filename)

        line = f.readline()
        if line.startswith("#"):
            # first line in the tstat tcp complete is not an actual data, it is just a header information.
            line = f.readline()
	    self.total = 1
            #curl_insert is inserting commands to influxDB with HTTP API
            curl_insert = "curl -i -XPOST 'http://"+config.CONFIG['host']+":"+str(config.CONFIG['port'])+"/write?db="+config.CONFIG['dbname']+"' -u "+config.CONFIG['id']+":"+config.CONFIG['password']+" --data-binary '"
            while True:

                if not line:
                    break
                record = tstat.tstatrecord(line)

                if record.err is not True:
                    #format of timstamp in log_tcp_complete is 'xxx~.xxxx'
                    #The valid format of epoch time in influxDb is 19 digits
                    epoch = (record.timestamp).replace(".","")
                    payload = record.s2c_payload
                    window = record.server_window_scale
                    rtt = record.s2c_average_round_trip_time
                    duration = record.completion_duration_time
                    retransmission = record.s2c_retransmission

                    curl_insert += 'log_tcp_complete,host='+record.sip+' s2c_payload='+payload+',s2c_retransmission='+retransmission+',server_window_scale='+window+',completion_duration_time='+duration+',s2c_average_round_trip_time='+rtt+' '+epoch+'\n'
                else:
                    if record.err_code == 1:
                        print('line number: '+str(self.total+1)+' in '+filename+'\n')
                        self.total_err += 1

                self.total += 1
                line = f.readline()

	    curl_insert += "' >/dev/null 2>&1"
            run.interact(self, curl_insert, db)
        f.close()

    def interact(self, curl_str, db):
        db.insert(curl_str)

    def error_handle(self, code):
        if code == 1:
            print('Broken Log File')
        elif code == 2:
            print('Port No.22')
        else:
            print('Unknown Err')
