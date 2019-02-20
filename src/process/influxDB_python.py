# -*- coding: utf-8 -*-
#!/opt/python/bin/python2.7

import os

class database():
    """database"""

    insert_query = "curl -i -XPOST 'http://%s:%s/write?db=%s' -u %s:%s --data-binary '"
    exist_query = 'curl -XPOST "http://%s:%s/query?db=%s" -u %s:%s --data-urlencode "q=SHOW FIELD KEYS"'
    create_query = 'curl -XPOST http://%s:%s/query -u %s:%s --data-urlencode "q=CREATE DATABASE %s" >/dev/null 2>&1'
    server_insert_query = 'server,host=%s,port=%s payload=%s,retransmission=%s,window_scale=%s,completion_duration_time=%s,average_round_trip_time=%s %s\n'
    client_insert_query = 'client,host=%s,port=%s payload=%s,retransmission=%s,window_scale=%s,completion_duration_time=%s,average_round_trip_time=%s %s\n'
    def __init__(self, host, port, user, pwd, dbname):

        #check if there exists database named dbname
        is_exist = os.popen(self.exist_query % (host, port, dbname, user, pwd)).read()

        if "error" in is_exist: #"error" in result string means that there is no database named dbname
            os.system(self.create_query % (host, port, user, pwd, dbname))
            self.is_exist = 0
        else:
            print('Database is already exists')
            self.is_exist = 1

    def insert(self, curl_str):
        run_curl = os.system(curl_str) #run the curl command
        return run_curl
