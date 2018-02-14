#!/opt/python/bin/python2.7

import os
import log_tcp_complete as tstat
from process import database
import config
import time

class run:
    
    total = 0
    total_err = 0

    def fileread(self,filename):
        f = open(filename)
        line = f.readline()
        if line.startswith("#"):
            #first line in the tstat tcp complete is not an actual data, it is just a header information.
            line = f.readline()

            while len(line.strip()) > 0:

                record = tstat.tstatrecord(line)

                if record.err is not True:
                    epoch = record.timestamp
                    #if run.time_constraint(self, epoch) is True:
                    run.interact(self, record, epoch)
                    #else:
                    #    print("time out")
                else:
                    run.error_handle(self, record.err_code)

                line = f.readline()
        f.close()
        print("END")


    def interact(self,record,epoch):
       	record = record.__dict__
       	db = database(config.CONFIG['host'],config.CONFIG['port'])
       	db.insert(record,epoch)

    def error_handle(self, code):
        if code == 1:
            print('Broken Log File')
        elif code == 2:
            print('Port No.22')
        else:
            print('Unknown Err')

    def time_constraint(self, epoch):
        current_time = float(time.time())
        if(current_time - epoch) <= config.CONFIG['time_constraint']:
            return True
        else:
            return False

def searchfile():
    total = 0
    total_err = 0
    path = os.path.expanduser(config.CONFIG['path'])
    # path = os.path.expanduser("~/PRAGMA")
    for root, dirs, files in os.walk(path):
        for dirname in dirs:
            ext = os.path.splitext(dirname)[1]
            if ext == '.out':
                full_dirname = os.path.join(path, dirname)
                # dirname will be the full path of .out dirs

                filenames = os.listdir(full_dirname)
                for filename in filenames:
                    if filename == 'log_tcp_complete':
                        full_filepath = os.path.join(full_dirname, filename)
                        # print full_filepath

                        print(full_filepath)
                        r = run()
                        r.fileread(full_filepath)
                        total += r.total
                        total_err += r.total_err
                        analyze(r.total, r.total_err)


def analyze(total, total_err):
    print('Total Number of Log process  : %d \nTotal Number of Err Occurred : %d' % (total, total_err))


searchfile()

