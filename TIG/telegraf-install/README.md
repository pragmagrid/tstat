### RUN THESE SCRIPTS WITH SU PERMISSION

Telegraf Installation script

```#!/bin/bash
curl -O https://raw.githubusercontent.com/pragmagrid/tstat/master/TIG/telegraf-install/telegraf-install.sh
```

How to use

```#!/bin/bash
curl -O https://raw.githubusercontent.com/pragmagrid/tstat/master/TIG/telegraf-install/telegraf-install.sh
chmod +x ./telegraf-install.sh
./telegraf-install.sh
```

Without configuration

```#!/bin/bash
./telegraf-install.sh
```

With custom configuration

```#!/bin/bash
curl -O https://raw.githubusercontent.com/pragmagrid/tstat/master/TIG/telegraf-install/telegraf.config.example
./telegraf-install.sh telegraf.config.example
```
