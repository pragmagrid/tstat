# $Id$
#
# @Copyright@
# @Copyright@
#

REDHAT.ROOT = $(CURDIR)/../../

-include $(ROCKSROOT)/etc/Rules.mk
include Rules.mk

FDTSCRIPTS = $(NAME)-server.sh $(NAME)-client.sh

SEDSPEC += -e 's%@PKGROOT@%$(PKGROOT)%g' 

%: %.in
	$(SED) $(SEDSPEC) $^ > $@

.SUFFIXES:

build: $(FDTSCRIPTS)
	
install::
	mkdir -p $(ROOT)/$(PKGROOT)/bin
	mkdir -p $(ROOT)/$(PKGROOT)/lib
	cp  $(NAME).jar $(ROOT)/$(PKGROOT)/lib
	install -m 755 $(FDTSCRIPTS) $(ROOT)/$(PKGROOT)/bin
	
clean::
	rm -rf $(FDTSCRIPTS)
