#!/opt/python/bin/python2.7

import os, sys
import config
from process import run
from influxDB_python import database
import time, datetime

def searchfile():

    total = 0
    total_err = 0
    path = os.path.expanduser(config.CONFIG['path'])

    host = config.CONFIG['host']
    port = config.CONFIG['port']
    user = config.CONFIG['id']
    password = config.CONFIG['password']
    dbname = config.CONFIG['dbname']
    start = sys.argv[1]
    end = sys.argv[2]
    is_all = False

    if start == None:
        is_all = True
    now = datetime.datetime.now()
    progress_file = config.CONFIG['file_list_path']+"/progress_"+now.strftime('%Y-%m-%d_%H:%M:%S')+".txt"
    progressed_log_file = open(config.CONFIG['file_list_path']+"/progress_"+now.strftime('%Y-%m-%d_%H:%M:%S')+".txt", 'w')
    progressed_log_file.write('Processing from '+start+' to '+end+'\n')
    progressed_log_file.close()
 
    db = database(host, port, user, password, dbname)
    
    start_time = time.time() #If you want to measure the actual running time of this program, you can use it.
    
    is_process = 0
    r = run()
    for out_dir in sorted(os.listdir(path)):
        if is_all:
            out_dir_path = path + "/" + out_dir
            file_path = out_dir_path + "/log_tcp_complete"
            
            r.fileread(file_path, out_dir, db, progress_file)

        else:
            if out_dir.startswith(start):
                is_process = 1
            elif out_dir.startswith(end):
                is_process = 2
            if is_process == 1 or is_process == 2:
                if is_process == 2 and out_dir.startswith(end) == False:
                    break
                out_dir_path = path + "/" + out_dir
                file_path = out_dir_path + "/log_tcp_complete"
            
                r.fileread(file_path, out_dir, db, progress_file)

            
    total = r.total
    total_err = r.total_err

    analyze(total, total_err)

    end_time = time.time()
    running_time = int(end_time - start_time)
    print('Total Running time : {:02d}:{:02d}:{:02d}'.format(running_time // 3600, (running_time % 3600 // 60), running_time % 60))

def analyze(total, total_err):
    print('Total Number of Log process  : %d \nTotal Number of Err Occurred : %d\n' % (total, total_err))

searchfile()
