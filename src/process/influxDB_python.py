# -*- coding: utf-8 -*-
#!/opt/python/bin/python2.7

import config
import time
import os

class database():
    """database"""

    def __init__(self, host, port, user, pwd, dbname):

        #check if there exists database named dbname
        is_exist = os.popen('curl -XPOST "http://'+host+':'+str(port)+'/query?db='+dbname+'" -u '+user+':'+pwd+' --data-urlencode "q=SHOW FIELD KEYS"').read()

        if "error" in is_exist: #"error" in result string means that there is no database named dbname
            os.system('curl -XPOST http://'+host+':'+str(port)+'/query -u '+user+':'+pwd+' --data-urlencode "q=CREATE DATABASE '+dbname+'" >/dev/null 2>&1')
            self.is_exist = 0
        else:
            print('Database is already exists')
            self.is_exist = 1

    def insert(self, curl_str):
        run_curl = os.system(curl_str) #run the curl command 
