#!/bin/bash
#
# @Copyright@
# @Copyright@
#
# set google url for dowloading sources
#export SURL="https://drive.google.com/open?id="

# download sources
. /opt/rocks/share/devel/src/roll/etc/bootstrap-functions.sh

# install prerequisites for building libpcap library
yum --enablerepo=base install libpcap-devel

# extract doc files for making userguide 
(cd src/tstat; make prepfiles)

