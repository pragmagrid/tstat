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

    for root, dirs, files in os.walk(path):

        for dirname in dirs:
            ext = os.path.splitext(dirname)[1]

            if ext == '.out':
                full_dirname = os.path.join(path, dirname)

                if full_dirname in list_written_directories:
                    print(full_dirname + ' : already in here')
                else:

                    filenames = os.listdir(full_dirname)
                    #list of files in current directory

                    for filename in filenames:

                        if filename == 'log_tcp_complete':
                            full_filepath = os.path.join(full_dirname, filename)
                            # print(full_filepath, full_dirname)

                            r = run()
                            r.fileread(full_filepath, full_dirname)

                            total += r.total
                            total_err += r.total_err

                            analyze(r.total, r.total_err)


def analyze(total, total_err):
    print('Total Number of Log process  : %d \nTotal Number of Err Occurred : %d' % (total, total_err))


searchfile()
