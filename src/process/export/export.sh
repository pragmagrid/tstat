#!/bin/sh

JSON_NAME=TSTAT.json

curl -i -X GET http://pc-170.calit2.optiputer.net:8080/chronograf/v1/dashboards/3 > "$JSON_NAME"
