#!/opt/python/bin/python2.7

import os
import log_tcp_complete as tstat
from process import database
import config
import time

class run:

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
                    if run.time_constraint(self, epoch) is True:
                        run.interact(self, record, epoch)
                    else:
                        print("time out")
                else:
                    print("error")

                line = f.readline()
        f.close()
        print("END")


    def interact(self,record,epoch):
       	record = record.__dict__
       	db = database(config.CONFIG['host'],config.CONFIG['port'])
       	db.insert(record,epoch)

    def time_constraint(self, epoch):
        current_time = float(time.time())
        if(current_time - epoch) <= config.CONFIG['time_constraint']:
            return True
        else:
            return False

def searchfile():
        path = os.path.expanduser(config.CONFIG['path'])
        for root, dirs, files in os.walk(path):
            for dirname in dirs:
                ext = os.path.splitext(dirname)[1]
                if ext == '.out':
                    full_dirname = os.path.join(path, dirname)
                    # dirname will be the full path of .out dirs

                    filenames = os.listdir(full_dirname)
                    for filename in filenames:
                        if filename == 'log_tcp_complete':
                            full_filepath = os.path.join(full_dirname,filename)
                            #print full_filepath

                            print(full_filepath)
                            r = run()
                            r.fileread(full_filepath)



searchfile()

