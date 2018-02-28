#!/bin/sh

#influxDB port
SRC=http://pc-170.calit2.optiputer.net:8086/query
ID=admin
PWD=admin

curl -XPOST $SRC --data-urlencode "q=CREATE USER "$ID" WITH PASSWORD '"$PWD"' WITH ALL PRIVILEGES"

