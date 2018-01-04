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
    wget  http://tstat.polito.it/download/tstat-3.1.1.tar.gz
    wget http://monalisa.cern.ch/FDT/lib/fdt.jar
    wget https://dl.influxdata.com/influxdb/releases/influxdb-1.4.2.x86_64.rpm


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

.. _Tstat : http://tstat.polito.it
.. _Tstat logs files structure: http://tstat.polito.it/measure.shtml#LOG
.. _Tstat logs post processing: https://github.com/straverso/tstat-post-processing
.. _Fast Data Transfer - FDT: http://monalisa.cern.ch/FDT
.. _FDT examples: http://monalisa.cern.ch/FDT/documentation_examples.html
.. _InfluxData products: https://www.influxdata.com/products/
.. _InfluxDB : https://www.influxdata.com/time-series-platform/influxdb/
.. _Chronograph : https://www.influxdata.com/time-series-platform/chronograf/
.. _Kapacitor : https://docs.influxdata.com/kapacitor/v1.4/introduction/getting_started/

