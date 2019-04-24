### RUN THESE SCRIPTS WITH SU PERMISSION

Installation script

```#!/bin/bash
curl -O https://raw.githubusercontent.com/kennaruk/centos-grafana-influx-sandbox/master/influxdb-install/influxdb-install.sh
```

How to use

```#!/bin/bash
curl -O https://raw.githubusercontent.com/kennaruk/centos-grafana-influx-sandbox/master/influxdb-install/influxdb-install.sh
chmod +x ./influxdb-install.sh
./influxdb-install.sh
```

Without configuration

```#!/bin/bash
./influxdb-install.sh
```

With custom configuration

```#!/bin/bash
curl -O https://raw.githubusercontent.com/kennaruk/centos-grafana-influx-sandbox/master/influxdb-install/influxdb.config.example
./influxdb-install.sh influxdb.config.example
```
