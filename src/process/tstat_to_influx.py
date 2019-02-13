#!/opt/python/bin/python2.7

import os
import config
from process import run
from influxDB_python import database
import time

def searchfile():

    total = 0
    total_err = 0
    path = os.path.expanduser(config.CONFIG['path'])

    host = config.CONFIG['host']
    port = config.CONFIG['port']
    user = config.CONFIG['id']
    password = config.CONFIG['password']
    dbname = config.CONFIG['dbname']
    start = config.CONFIG['start_file']
    end = config.CONFIG['end_file']

    progressed_log_file = open(config.CONFIG['file_list_path']+"/progress.txt", 'w')
    progressed_log_file.write('Processing from '+start+' to '+end+'\n')
    progressed_log_file.close()
 
    db = database(host, port, user, password, dbname)
    
    start_time = time.time() #If you want to measure the actual running time of this program, you can use it.
    
    is_process = 0
    r = run()
    for out_dir in sorted(os.listdir(path)):
        
        if out_dir == start:
            is_process = 1
        if is_process == 1:
            out_dir_path = path + "/" + out_dir
            file_path = out_dir_path + "/log_tcp_complete"
            
            r.fileread(file_path, out_dir, db)

        if out_dir == end:
            break
    total = r.total
    total_err = r.total_err

    analyze(total, total_err)

    end_time = time.time()
    running_time = int(end_time - start_time)
    print('Total Running time : {:02d}:{:02d}:{:02d}'.format(running_time // 3600, (running_time % 3600 // 60), running_time % 60))

def analyze(total, total_err):
    print('Total Number of Log process  : %d \nTotal Number of Err Occurred : %d\n' % (total, total_err))

searchfile()
