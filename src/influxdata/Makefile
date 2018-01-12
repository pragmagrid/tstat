#
### @Copyright@
### @Copyright@
#
 
REDHAT.ROOT     = $(CURDIR)/../../
MAKE.iscontrib  = 1
-include $(ROCKSROOT)/etc/Rules.mk
include Rules.mk

rpm:: build
	-cp *.$(ARCH).rpm $(REDHAT.RPMS)/$(ARCH)/

build:
	mkdir -p $(REDHAT.RPMS)/$(ARCH)/
