# $Id$
#
# @Copyright@
# @Copyright@
#

REDHAT.ROOT = $(CURDIR)/../../

-include $(ROCKSROOT)/etc/Rules.mk
include Rules.mk

# Option --enable-rrdthread works on kernels > 2.6.35
# use foundaton-rrdtool, specify *FLAGS below
TSTATOPTS = --enable-libtstat --enable-zlib LDFLAGS=-L/opt/rocks/lib CFLAGS=-I/opt/rocks/include

%: %.in
	$(SED) $(SEDSCRIPT) $^ > $@

prepfiles: files.list
	gunzip < $(NAME)-$(VERSION).$(TARBALL_POSTFIX) | tar -x -v --files-from files.list -f -
	mv $(NAME)-$(VERSION)/doc/HOWTO/* ../guide
	rm -rf $(NAME)-$(VERSION)/doc/HOWTO

build:
	tar xzvf  $(NAME)-$(VERSION).$(TARBALL_POSTFIX) 
	( 							\
		cd $(NAME)-$(VERSION);				\
		./autogen.sh;         				\
		./configure --prefix=$(PKGROOT) $(TSTATOPTS);	\
		$(MAKE);					\
	)
	
install::
	mkdir -p $(ROOT)/$(PKGROOT)
	(							\
		cd $(NAME)-$(VERSION);				\
		$(MAKE) prefix=$(ROOT)/$(PKGROOT) install;\
	)
	cp -r $(NAME)-$(VERSION)/doc $(ROOT)/$(PKGROOT)
	cp -r $(NAME)-$(VERSION)/tstat-conf $(ROOT)/$(PKGROOT)
	
clean::
	rm -rf $(NAME)-$(VERSION)
	rm -rf files.list
