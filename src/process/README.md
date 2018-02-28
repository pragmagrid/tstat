## Local Env

##### Python 2.7

##### InfluxDB 1.4

> For influxDB 8086 port used

##### Chronograph 1.4

> Instead of 8888 which is default, 8080 port has been used

## Setup

##### Start InfluxDB

> /etc/rc.d/init.d/influxdb start

##### Start Chronograph

> /etc/rc.d/init.d/chronograf start

## Classes

##### config.py

> For configurations

##### log_tcp_complete.py

> This class will parse tstat and gather certain datas and make as one big object
> If other fields in tstat is needed then give change in this class

##### process.py

> with parsed object from log_tcp_complete, it process to InfluxDB

##### influxDB_python

> This will be called by process, and in this class connection to the InfluxDB is set.
> Here datas will be written into the connected InfluxDB.

##### main.py

> main class which checks directories that have not processed and will call process.py for process

##### setup_admin.sh

> create admin user with input ID and PWD

## Run

1. run setup_admin.sh (it will setup authentication by making admin user)
2. goto chronograf webpage -> InfluxDB Admin -> Users (check if there is an admin user have created)
3. open InfluxDB.conf -> Search [http] -> uncomment auth-enabled -> change the value from false to true (default is false)
> /etc/influxdb/influxdb.conf
4. open telegraf.conf -> Search [Output] -> InfluxDB -> set username = [admin username that you made], password = [admin password that you set]
> /etc/telegraf/telegraf.conf
5. open conf.py -> type username, password
6. run main.py with ./main.py

Follow step 1 ~ 5 when first running this program, from second time just step 6 will do.


## Configuration for other env

Do not make change directly to the python files!

To Change chronograf port number, unfortunately there is no external config file.

Therefore set env PORT = 'whatever port number' or set the switch --port 'whatever port number'.

Anything else except chronograph port, make change in config.py.

## Naming Schema

Prefer to be specific and meaningful name for variable and functions.

If there are more than a word, naming will be word1_word2.

## log Track

progress.txt will be made as you run this program.

In progress.txt the directories that have been insulted properly into the InfluxDB will be recorded so that there are no waste of process.

## Useful Reference

##### User Authentication

> https://docs.influxdata.com/influxdb/v1.4/query_language/authentication_and_authorization/#set-up-authentication

> https://docs.influxdata.com/chronograf/v1.4/administration/managing-influxdb-users/#step-3-create-an-admin-user

##### Chronograph pre-created Dashboards

> https://github.com/influxdata/chronograf

##### Tstat Structure

> http://tstat.polito.it/measure.shtml#LOG

> log_tcp_complete.py only parse window size, time (duration of the transfer), total bytes transmitted, retransmits, average rount trip time

> log_tcp_complete_all.py will parse every fields (reference : https://github.com/straverso/tstat-post-processing)
