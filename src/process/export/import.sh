#!/bin/sh

DST=http://pc-170.calit2.optiputer.net:8080/chronograf/v1/dashboards
FILE=/export/home/minsung/python/export/TSTAT.json

curl -i -X POST -H "Content-Type: application/json" \
$DST \
-d @"$FILE"
