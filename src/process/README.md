## Local Env

##### Python 2.7

##### InfluxDB 1.4

> For influxDB 8086 port used

## Setup

##### Start InfluxDB on Server

> /etc/rc.d/init.d/influxdb start

##### Install Grafana on Server

> Folow the Grafana documentations.(http://docs.grafana.org/installation/rpm/)
> I installed with wget command. (wget https://dl.grafana.com/oss/release/grafana-5.4.2-1.x86_64.rpm)

##### Start Grafana on Server

> sudo service grafana-server start

##### Port forwarding on local

> Run 'ssh -L 3000:localhost:3000 user@host' on local to open grafana browser. It's port forwarding (Host's port number 3000 is forwarded to localhost's 3000). The reason why this command need is written at tstat/week_plan/JAN_WK_4th.md.
 
## Python codes

##### config.py

> For configurationss

##### log_tcp_complete.py

> This class will parse tstat and gather certain datas and make as one big object
> If other fields in tstat is needed then give change in this class

##### process.py

> with parsed object from log_tcp_complete, it process to InfluxDB with HTTP API.

##### influxDB_python.py

> This will be called by tstat_to_influx.py at initial, and check if database named by config.py exists in influxDB.
> Here datas will be written into the connected InfluxDB via being called by process.py.

##### tstat_to_influx.py

> Main class which checks directories that start file and end file which are set by input arguments at running and will call process.py for process

##### Naming Schema

> Prefer to be specific and meaningful name for variable and functions. If there are more than a word, naming will be word1_word2.

## Run

1. Open InfluxDB.conf and look for 'http'. Uncomment 'auth-enabled' and change the value from false to true (default is false)
> /etc/influxdb/influxdb.conf
2. Open grafana page in browser and go to 'grafana page > Configuration > Server Admin > Orgs'. Set the organization name.
3. Open grafana.conf and look for 'anonymous'. Change the values follow tstat/week_plan/JAN_WK_5th.md. Look for 'auth.basic' and change 'enabled' value false.
> /etc/grafana/grafana.ini
4. Open conf.py and type id, password, dbname and port that is used to connect to influxDB. And type host, path where log files are and file_list_path which is path to store the error log. Finaly, type the line_limit that is limit line number processed at once.
6. Run main.py with './tstat_to_influx.py beginning_time end_time'.
> ./tstat_to_influx.py 2018_12 2019_01
or
> ./tstat_to_influx.py 2018_12_30 2019_01_24
and also the program can be run with YYYY_MM_DD_HH or YYYY_MM_DD_HH_MM.
If the beginning_time and end_time is empty, then the program will process from the first log file of all to the last log file of all. 

## How to create dashboard on Grafana

> Fisrt of all, there's need to configure the 'Data Sources'. Open the grafana page in browser (localhost:3000) and move the mouse cursor to the gear wheel shape button at the left. Then, the sub menu will be spread out. Click the 'Data Sources' and click the 'Add Data Source' green button. Then, there are some different types. Just click the 'InfluxDB' button. Fill the each part with each proper information.
> Then, there's ready to create dashboard. Go back Grafana main page and move the mouse cursor to the plus shape button at the left. The sub menu are Dashboard, Folder and Import. Click the 'Dashboard'. And add the pannel whatever the form you want, it's done.
> The detail description is on Grafana documentation (http://docs.grafana.org/guides/getting_started/)

## log Track

progress_runningtime.txt will be made whenever you run this program.

In progress_runningtime.txt, the line number and error type are written.

## Useful Reference

##### User Authentication

> https://docs.influxdata.com/influxdb/v1.4/query_language/authentication_and_authorization/#set-up-authentication

> https://docs.influxdata.com/chronograf/v1.4/administration/managing-influxdb-users/#step-3-create-an-admin-user

##### Access Grafana without login

> http://docs.grafana.org/auth/overview/#anonymous-authentication


##### Tstat Structure

> http://tstat.polito.it/measure.shtml#LOG

> log_tcp_complete.py only parse window size, time (duration of the transfer), total bytes transmitted, retransmits, average rount trip time

> log_tcp_complete_all.py will parse every fields (reference : https://github.com/straverso/tstat-post-processing)
