#!/opt/python/bin/python2.7

import log_tcp_complete as tstat
import time
import config

class run:

    total = 0
    total_err = 0

    #curl_insert is inserting commands with server's information to influxDB with HTTP API
    curl_insert = "curl -i -XPOST 'http://"+config.CONFIG['host']+":"+str(config.CONFIG['port'])+"/write?db="+config.CONFIG['dbname']+"' -u "+config.CONFIG['id']+":"+config.CONFIG['password']+" --data-binary '"
    count = 0

    def fileread(self, filename, dirname, db, progress_file):

        progress_f = open(progress_file, 'a')

        f = open(filename)
        line = f.readline()

        if line.startswith("#"):
            # first line in the tstat tcp complete is not an actual data, it is just a header information.
            line = f.readline()
            self.line = 1

            while True:

                if not line:
                    break
                record = tstat.tstatrecord(line)

                if record.err is not True:
                    #format of timstamp in log_tcp_complete is 'xxx~.xxxx'
                    #The valid format of epoch time in influxDB is 19 digits
                    epoch = (record.timestamp).replace(".","")
                    duration = record.completion_duration_time

                    self.curl_insert += db.server_insert_query % (record.sip, record.server_port, record.s2c_payload, record.s2c_retransmission, record.server_window_scale, duration, record.s2c_average_round_trip_time, epoch)
                    self.curl_insert += db.client_insert_query % (record.cip, record.client_port, record.c2s_payload, record.c2s_retransmission, record.client_window_scale, duration, record.c2s_average_round_trip_time, epoch)
                    self.count += 2
        
                else:
                    if record.err_code == 1:
                        progress_f.write('#line number: '+str(self.line+1)+' in '+filename+'\n Length is less than 130.\n')
                    elif record.err_code == 2:
                        progress_f.write('#line number: '+str(self.line+1)+' in '+filename+'\n Port num of server is 22.\n')
                    else :
                        progress_f.write('#line number: '+str(self.line+1)+' in '+filename+'\n Port num of client is 22.\n')
                    self.total_err += 1
                
                self.line += 1
                
                if self.count == config.CONFIG['line_limit']:
                    #This additional command is for not printing the result of process on console.
                    run.interact(self, self.curl_insert, db)

                line = f.readline()
            
            if self.count > 0:
                run.interact(self, self.curl_insert, db)
        f.close()
        progress_f.close()

    def interact(self, curl_str, db):
        self.total += (self.count/2)
        curl_str += "' >/dev/null 2>&1"
        db.insert(curl_str)
        self.curl_insert = db.insert_query % (config.CONFIG['host'], config.CONFIG['port'], config.CONFIG['dbname'], config.CONFIG['id'], config.CONFIG['password'])
        self.count = 0

    def error_handle(self, code):
        if code == 1:
            print('Broken Log File')
        elif code == 2:
            print('Port No.22')
        else:
            print('Unknown Err') 
