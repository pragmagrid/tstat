#!/opt/python/bin/python2.7

import log_tcp_complete as tstat
import time
import config

class run:

    total = 0
    total_err = 0

    def fileread(self, filename, dirname, db):

        base_curl = "curl -i -XPOST 'http://"+config.CONFIG['host']+":"+str(config.CONFIG['port'])+"/write?db="+config.CONFIG['dbname']+"' -u "+config.CONFIG['id']+":"+config.CONFIG['password']+" --data-binary '"

        f = open(filename)
        line = f.readline()

        if line.startswith("#"):
            # first line in the tstat tcp complete is not an actual data, it is just a header information.
            line = f.readline()
	    self.total = 1
            #curl_insert is inserting commands with server's information to influxDB with HTTP API
            curl_insert = base_curl

            while True:

                if not line:
                    break
                record = tstat.tstatrecord(line)

                if record.err is not True:
                    #format of timstamp in log_tcp_complete is 'xxx~.xxxx'
                    #The valid format of epoch time in influxDB is 19 digits
                    epoch = (record.timestamp).replace(".","")
                    s_payload = record.s2c_payload
                    s_window = record.server_window_scale
                    s_rtt = record.s2c_average_round_trip_time
                    duration = record.completion_duration_time
                    s_retransmission = record.s2c_retransmission
                    c_payload = record.c2s_payload
                    c_window = record.client_window_scale
                    c_rtt = record.c2s_average_round_trip_time
                    c_retransmission = record.c2s_retransmission
                    s_port = record.server_port
                    c_port = record.client_port

                    curl_insert += 'log_tcp_complete,s_host='+record.sip+',s_port='+s_port+',c_host='+record.cip+',c_port='+c_port+' s2c_payload='+s_payload+',s2c_retransmission='+s_retransmission+',server_window_scale='+s_window+',completion_duration_time='+duration+',s2c_average_round_trip_time='+s_rtt+',c2s_retransmission='+c_retransmission+',client_window_scale='+c_window+',c2s_average_round_trip_time='+c_rtt+' '+epoch+'\n'
                    
                else:
                    if record.err_code == 1:
                        progress_file = open(config.CONFIG['file_list_path']+"/progress.txt", 'a')
                        progress_file.write('line number: '+str(self.total+1)+' in '+filename+'\n')
                        progress_file.close()
                        self.total_err += 1
                
                self.total += 1
                line = f.readline()
            
           #This additional command is for not printing the result of process on console.
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
