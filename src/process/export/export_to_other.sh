#!/bin/sh

DASHBOARD_NAME=test
#name of the DASHBOARD to make in DST

DST=http://naver.com:8888/chronograf/v1/dashboards
SRC=http://pc-170.calit2.optiputer.net:8080/chronograf/v1/dashboards

curl -Ss $SRC|/export/home/minsung/jq-linux64 -r '.dashboards[]|@json' |while IFS= read -r dashboard; do echo $dashboard > "$DASHBOARD_NAME"; curl -X POST -H "Accept: application/json" -d @"$DASHBOARD_NAME" $DST; done
