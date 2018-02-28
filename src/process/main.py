#!/opt/python/bin/python2.7

import os
import config
from process import run

def searchfile():

    total = 0
    total_err = 0
    path = os.path.expanduser(config.CONFIG['path'])
    list_written_directories = []


    if os.path.isfile(config.CONFIG['file_list_path']+"/progress.txt"):
        written_directories = open(config.CONFIG['file_list_path']+"/progress.txt", 'r')
        temp = written_directories.read()
        written_directories.close()
        list_written_directories = temp.split()


    #print(list_written_directories)
    for out_dir in sorted(os.listdir(path)):

            if not out_dir.startswith("."):

                out_dir_path = path + "/" + out_dir

                if out_dir_path in list_written_directories:
                    print(out_dir_path + ' : already in here')

                else:

                    for filename in os.listdir(out_dir_path):

                        if filename == 'log_tcp_complete':

                            file_path = out_dir_path + "/" + filename

                            r = run()
                            r.fileread(file_path, out_dir_path)

                            total += r.total
                            total_err += r.total_err

                            analyze(r.total, r.total_err)

def analyze(total, total_err):
    print('Total Number of Log process  : %d \nTotal Number of Err Occurred : %d' % (total, total_err))


searchfile()
