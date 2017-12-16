# $Id$
#
# @Copyright@
# @Copyright@
#

REDHAT.ROOT = $(CURDIR)/../../

-include $(ROCKSROOT)/etc/Rules.mk
include Rules.mk

SCRIPTS = $(NAME)-server.sh $(NAME)-client.sh

build::
	
install::
	mkdir -p $(ROOT)/$(PKGROOT)/bin
	cp  $(NAME).jar $(ROOT)/$(PKGROOT)/bin
	install -m 755  $(SCRIPTS)  $(ROOT)/$(PKGROOT)/bin
	
clean::
