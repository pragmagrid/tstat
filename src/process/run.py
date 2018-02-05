#!/usr/local/bin/python2.7

import os
import log_tcp_complete_parts as tstat
# import process as database
from process import database
import config

class run:

    def fileread(self,filename):
        f = open(filename)
        #f = open (os.path.expanduser("~/2018_01_11_14_48.out/log_tcp_complete"))
        line = f.readline()
        if line.startswith("#"):
            #first line in the tstat tcp complete is not an actual data, it is just a header information.
            line = f.readline()

            while len(line.strip()) > 0:

                record = tstat.tstatrecord(line)
                if record.err is not True:
                    run.interact(self,record)
                    line = f.readline()
                else:
                    print("1")
                    break;

        # record = tstat.tstatrecord(line)
        f.close()
        # run.interact(self,record)
        print("END")


    def interact(self,record):
        record = record.__dict__
        # print(record)
        # json_record = json.dumps(record.__dict__)
        # print(json_record)
        db = database(config.CONFIG['host'],8086)
        # db = database('localhost',8086)
        db.insert(record)

def searchfile():
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
                            full_filepath = os.path.join(full_dirname,filename)
                            #print full_filepath

                            print(full_filepath)
                            r = run()
                            r.fileread(full_filepath)



searchfile()
