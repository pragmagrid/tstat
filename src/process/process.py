#!/opt/python/bin/python2.7

import log_tcp_complete as tstat
import time
from influxDB_python import database
import config

class run:

    total = 0
    total_err = 0

    def fileread(self, filename, dirname):

        f = open(filename)

        line = f.readline()
        if line.startswith("#"):
            # first line in the tstat tcp complete is not an actual data, it is just a header information.
            line = f.readline()
            self.total += 1
            while len(line.strip()) > 0:

                record = tstat.tstatrecord(line)

                if record.err is not True:
                    epoch = record.timestamp
                    # if run.time_constraint(self, epoch) is True:
                    run.interact(self, record, epoch)
                    # else:
                    #     print("time out")
                else:
                    run.error_handle(self, record.err_code)
                    self.total_err += 1

                line = f.readline()
                self.total += 1

        f.close()
        print("END")

        f = open(config.CONFIG['file_list_path']+"/progress.txt", 'a')
        f.write(dirname+'\n')
        f.close()

    def interact(self, record, epoch):
        record = record.__dict__
        db = database(config.CONFIG['host'], config.CONFIG['port'])
        db.insert(record, epoch)

    def error_handle(self, code):
        if code == 1:
            print('Broken Log File')
        elif code == 2:
            print('Port No.22')
        else:
            print('Unknown Err')

    def time_constraint(self, epoch):
        current_time = float(time.time())
        if (current_time - epoch) <= config.CONFIG['time_constraint']:
            return True
        else:
            return False

