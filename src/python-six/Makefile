# $Id$
#
# @Copyright@
# @Copyright@
#

REDHAT.ROOT = $(CURDIR)/../../

-include $(ROCKSROOT)/etc/Rules.mk
include Rules.mk

PY.PATH = /opt/python/bin/python2.7

build:
	tar xzf  $(ARCHIVENAME)-$(VERSION).$(TARBALL_POSTFIX)
	(\
	    cd $(ARCHIVENAME)-$(VERSION);   \
	    $(PY.PATH) setup.py build;      \
	)
	
install::
	(\
	    cd $(ARCHIVENAME)-$(VERSION);   \
	    $(PY.PATH) setup.py $@ --root=$(ROOT)/; \
	)
	
clean::
	rm -rf $(ARCHIVENAME)-$(VERSION) 
