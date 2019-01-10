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

    db = database(host, port, user, password, dbname)
    if db.is_exist :
        print("Are you sure to use "+dbname+" database? (yes or no)")
        db_answer = raw_input() #If your python version is higher than 3, modify 'raw_input' to 'input'
        if db_answer == "no":
            return 0
        elif db_answer != "yes":
            return 0

    start_time = time.time() #If you want to measure the actual running time of this program, you can use it.
    start = 0 #If start is 0, do not read file and read next log file name until reaching the file which is last worked previously

    #Read the name of log file which is last worked previously.
    if os.path.isfile(config.CONFIG['file_list_path']+"/progress.txt"): #It means that there is a history of previous work.
        f = open(config.CONFIG['file_list_path']+"/progress.txt", 'r')
        finished_file = f.read() #finished_file is name of log file which is last worked previously.
    else: #If it is first time to run this program,
        start = 1 #If start is 1, read file, process and insert to influxDB.

    for out_dir in sorted(os.listdir(path)):
        if start == 1:
            out_dir_path = path + "/" + out_dir
            file_path = out_dir_path + "/log_tcp_complete"

            r = run()
            r.fileread(file_path, out_dir_path, db)

            total += r.total
            total_err += r.total_err
        elif out_dir == finished_file: #If it reaches on last worked log file,
            start = 1 #The follow log files is processed. 

    progressed_log_file = open(config.CONFIG['file_list_path']+"/progress.txt", 'w') #Save the file name which is last worked.
    progressed_log_file.write(out_dir)
    progressed_log_file.close()
    
    analyze(total, total_err)

    end_time = time.time()
    running_time = int(end_time - start_time)
    print('Total Running time : {:02d}:{:02d}:{:02d}'.format(running_time // 3600, (running_time % 3600 // 60), running_time % 60))

def analyze(total, total_err):
    print('Total Number of Log process  : %d \nTotal Number of Err Occurred : %d\n' % (total, total_err))

searchfile()
