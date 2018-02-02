# -*- coding: utf-8 -*-
"""Tutorial on using the InfluxDB client."""

import argparse
import json
from datetime import datetime

from influxdb import InfluxDBClient


class database():
    """database"""

    def __init__(self, host, port):
        self.host = host
        self.port = port

    def insert(self, jsons):
        """Instantiate a connection to the InfluxDB.
        """
        user = 'root'
        password = 'root'
        dbname = 'test'
        query = 'select value from log_tcp_complete;'
        current_time = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
        json_body = [
            {
                "measurement": "log_tcp_complete",
                "tags": {
                    "host": "server1",
                    "region": "us-west"
                },
                "time": current_time,
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

        print("Querying data: " + query)
        result = client.query(query)

        print("Result: {0}".format(result))
