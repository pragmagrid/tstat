Tstat Roll
===========

.. contents::

Introduction
-------------
This roll installs TCP statistical and analysis tool ``tstat``

Downloads
-----------
::

    wget http://tstat.polito.it/download/tstat_rrd.cgi
    wget http://tstat.polito.it/download/tstat-3.1.1.tar.gz
    wget http://monalisa.cern.ch/FDT/lib/fdt.jar
    wget https://dl.influxdata.com/influxdb/releases/influxdb-1.4.2.x86_64.rpm
    wget https://dl.influxdata.com/chronograf/releases/chronograf-1.4.0.1.x86_64.rpm
    wget https://dl.influxdata.com/kapacitor/releases/kapacitor-1.4.0.x86_64.rpm
    wget https://dl.influxdata.com/telegraf/releases/telegraf-1.5.1-1.x86_64.rpm

Github repo for a python client for influxdb ias available at `influxdb-python`_.
Get latest release v.5.0.0 (as of Jan 2018) ::

    wget https://github.com/influxdata/influxdb-python/archive/v5.0.0.tar.gz

influxdb-python dependencies ::

    for influxdb 
        pytz: https://pypi.python.org/pypi/pytz
        dateutil: https://pypi.python.org/pypi/python-dateutil
        requests: wget https://github.com/requests/requests/archive/v2.18.4.tar.gz

    for requests: 
        urllib3: https://pypi.python.org/pypi/urllib3
        chardet: https://pypi.python.org/pypi/chardet
        certifi: https://pypi.python.org/pypi/certifi
        idna: https://pypi.python.org/pypi/certifi


NOTE: influxdb-python may not work with influxdb RPM version 1.4.2 but is stateds to work with 
version  1.2.4. Both RPMs are available in the roll.



Links
---------

#. `Tstat`_
#. `Tstat logs post processing`_
#. `Tstat logs files structure`_
#. `Fast Data Transfer - FDT`_
#. `FDT examples`_
#. `InfluxData products`_ 

   + store data with `InfluxDB`_
   + graph and visualize data with `Chronograph`_
   + use custom logic with `Kapacitor`_


Building
---------

To build the roll, execute : ::

    # ./bootstarp.sh
    # make roll

The fisrt command downloads source distribution from doogle drive.
A successful build will create  ``tstat-*.x86_64*.iso`` file.


Installing
------------

To add this roll to the existing cluster, execute these instructions on a Rocks frontend: ::

    # rocks add roll tstat-*.x86_64.disk1.iso
    # rocks enable roll tstat
    # (cd /export/rocks/install; rocks create distro)
    # rocks run roll tstat > add-roll.sh
    # bash add-roll.sh

What is installed:
-------------------

#. The tstat software is installed in /opt/tstat 

#. A usersguide is provided with the distribution and  the files names are modified
   to fit the rocks roll documentation, otherwise all ithe info is intact. 
   Roll usersguide is installed in ``/var/www/html/roll-documentation/tstat``

Using
-------

Read the original users guide for inforation on how to create config files and run tstat.

#. To run with histogram:

   /opt/tstat/bin/tstat -N l.conf -l -i eth5 -H histo.conf -s traces

#. To Run with RRD :
   
   tstat -R -l -N l.conf -H histo.conf -i eth5 -s traces2 -r traces2

Using Chronograf
-------------------

See `Influxdata chronograf docs`_

.. _Tstat : http://tstat.polito.it
.. _Tstat logs files structure: http://tstat.polito.it/measure.shtml#LOG
.. _Tstat logs post processing: https://github.com/straverso/tstat-post-processing
.. _Fast Data Transfer - FDT: http://monalisa.cern.ch/FDT
.. _FDT examples: http://monalisa.cern.ch/FDT/documentation_examples.html
.. _InfluxData products: https://www.influxdata.com/products/
.. _InfluxDB : https://www.influxdata.com/time-series-platform/influxdb/
.. _Chronograph : https://www.influxdata.com/time-series-platform/chronograf/
.. _Kapacitor : https://docs.influxdata.com/kapacitor/v1.4/introduction/getting_started/
.. _influxdb-python : https://github.com/influxdata/influxdb-python
.. _Influxdata chronograf docs : https://docs.influxdata.com/chronograf/v1.4/introduction/getting-started/
