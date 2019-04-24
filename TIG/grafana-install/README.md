### RUN THESE SCRIPTS WITH SU PERMISSION

Installation script

```#!/bin/bash
curl -O https://raw.githubusercontent.com/pragmagrid/tstat/master/TIG/grafana-install/grafana-install.sh
```

How to use

```#!/bin/bash
curl -O https://raw.githubusercontent.com/pragmagrid/tstat/master/TIG/grafana-install/grafana-install.sh
chmod +x ./grafana-install.sh
./grafana-install.sh
```

Without configuration

```#!/bin/bash
./grafana-install.sh
```

With custom configuration

```#!/bin/bash
curl -O https://raw.githubusercontent.com/pragmagrid/tstat/master/TIG/grafana-install/grafana.config.example
./grafana-install.sh grafana.config.example
```
