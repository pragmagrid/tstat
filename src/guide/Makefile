# @Copyright@
# @Copyright@
#

PKGROOT         = /var/www/html/roll-documentation/$(ROLL)/$(VERSION)
REDHAT.ROOT     = $(PWD)/../../

-include $(ROCKSROOT)/etc/Rules.mk
include Rules.mk

html: 
	cat header.html HOWTO.html > index.html

build: html 

install:: build
	mkdir -p $(ROOT)/$(PKGROOT)/
	install -ma+r HOWTO.pdf 	$(ROOT)/$(PKGROOT)/$(NAME).pdf
	install -ma+r index.html    	$(ROOT)/$(PKGROOT)/
	install -ma+r tstat*.png	$(ROOT)/$(PKGROOT)

clean::
	rm -f index.html
