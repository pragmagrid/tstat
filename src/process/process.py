# -*- coding: utf-8 -*-

import config
import time
from influxdb import InfluxDBClient


class database():
    """database"""

    def __init__(self, host, port):
        self.host = host
        self.port = port

    def insert(self, jsons, epoch):
        """Instantiate a connection to the InfluxDB.
        """
        user = config.CONFIG['id']
        password = config.CONFIG['password']
        dbname = config.CONFIG['dbname']
	timestamp = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.localtime(epoch))
        json_body = [
            {
                "measurement": "log_tcp_complete",
                "tags": {
                    "host": config.CONFIG['hostname']
                },
                "time": timestamp,
                "fields": {
                }
            }
        ]

        json_body[0]['fields'] = jsons

        client = InfluxDBClient(self.host, self.port, user, password, dbname)

        print("Create database: " + dbname)
        client.create_database(dbname)

        print("Write points: {0}".format(json_body))
        client.write_points(json_body)

