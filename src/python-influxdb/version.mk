NAME = opt-influxdb
ARCHIVENAME = influxdb-python
VERSION = 5.0.0
RELEASE = 0

TARBALL_POSTFIX = tar.gz

RPM.EXTRAS = "AutoReq: no"

RPM.FILES = \
/opt/python/lib/python2.7/site-packages/influxdb-5.0.0* \n \
/opt/python/lib/python2.7/site-packages/influxdb/

