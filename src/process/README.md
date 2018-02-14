## Local Env

##### Python 2.7

##### InfluxDB 1.4

>For influxDB 8086 port used

##### Chronograph 1.4

>Instead of 8888 which is default, 8080 port has been used

## Setup

##### Start InfluxDB

>/etc/rc.d/init.d/influxdb start

##### Start Chronograph

>/etc/rc.d/init.d/chronograf start

## Run

./run.py


## Configuration for other env

Do not make change directly to the python files!

To Change chronograf port number, unfortunately there is no external config file.

Therefore set env PORT = 'whatever port number' or set the switch --port 'whatever port number'.

Anything else except chronograph port, make change in config.py.

## Naming Schema

Prefer to be specific and meaningful name for variable and functions.

If there are more than a word, naming will be word1_word2.
