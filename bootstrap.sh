#!/bin/bash
#
# @Copyright@
# @Copyright@
#
# set google url for downloading sources
export SURL="https://drive.google.com/open?id=1GhZuRdqWzE2mZTJ87UEL0tay-Yh9oCP8"

# download sources
. /opt/rocks/share/devel/src/roll/etc/bootstrap-functions.sh

# install prerequisites for building libpcap library
yum --enablerepo=base install libpcap-devel

# extract doc files for making userguide 
(cd src/tstat; make prepfiles)

