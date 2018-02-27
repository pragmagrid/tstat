# $Id$
#
# @Copyright@
# @Copyright@
#

REDHAT.ROOT = $(CURDIR)/../../

-include $(ROCKSROOT)/etc/Rules.mk
include Rules.mk


build:
	tar xzvf  $(NAME)-$(VERSION).$(TARBALL_POSTFIX) 
	( 							\
		cd $(NAME)-$(VERSION);				\
		./configure --disable-maintainer-mode --prefix=$(PKGROOT); \
		$(MAKE);					\
	)
	
install::
	mkdir -p $(ROOT)/$(PKGROOT)
	(							\
		cd $(NAME)-$(VERSION);				\
		$(MAKE) prefix=$(ROOT)/$(PKGROOT) install;\
	)
	
clean::
	rm -rf $(NAME)-$(VERSION)
	rm -rf files.list
